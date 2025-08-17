from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import *
from .serializers import *
from .serializers import LoginSerializer, UserCreateSerializer, UserSerializer

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'register':
            try:
                from .serializers import RegisterSerializer
                return RegisterSerializer
            except ImportError:
                return LoginSerializer  # fallback nếu chưa có RegisterSerializer
        return LoginSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        return Response(UserSerializer(request.user).data)

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Book.objects.filter(is_active=True).prefetch_related(
        'authors', 'categories', 'images', 'attributes', 'sellers__seller'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'short_description', 'authors__name']
    ordering_fields = ['created_at', 'rating_average', 'quantity_sold', 'list_price']
    filterset_fields = ['categories__id', 'authors__id', 'is_featured']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookListSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        books = self.get_queryset().filter(is_featured=True)[:8]
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        book = self.get_object()
        similar_books = self.get_queryset().filter(
            categories__in=book.categories.all()
        ).exclude(id=book.id).distinct()[:6]
        serializer = self.get_serializer(similar_books, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]

class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response({'items': serializer.data['items']})
    
    def get_cart(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @action(detail=False, methods=['get'])
    def cart_items(self, request):  # Đổi tên từ 'list' thành 'cart_items'
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response({'items': serializer.data['items']})
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        cart = self.get_cart()
        book_id = request.data.get('bookId')
        quantity = request.data.get('quantity', 1)
        
        try:
            book = Book.objects.get(id=book_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, book=book,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
    
    @action(detail=False, methods=['put'], url_path='(?P<book_id>[^/.]+)')
    def update_item(self, request, book_id=None):
        cart = self.get_cart()
        quantity = request.data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(cart=cart, book_id=book_id)
            cart_item.quantity = quantity
            cart_item.save()
            
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)
    
    @action(detail=False, methods=['delete'], url_path='(?P<book_id>[^/.]+)')
    def remove_item(self, request, book_id=None):
        cart = self.get_cart()
        try:
            cart_item = CartItem.objects.get(cart=cart, book_id=book_id)
            cart_item.delete()
            return Response(status=204)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        cart = self.get_cart()
        cart.items.all().delete()
        return Response(status=204)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__book')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'confirmed':
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'cancelled'})
        return Response({'error': 'Cannot cancel this order'}, status=400)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username']
    ordering_fields = ['created_at', 'email']