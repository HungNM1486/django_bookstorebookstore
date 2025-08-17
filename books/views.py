from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import *
from .serializers import *
from .serializers import LoginSerializer, UserCreateSerializer, UserSerializer, CategoryTreeSerializer
from .pagination import CustomPageNumberPagination

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
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'Đăng xuất thành công'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = Book.objects.filter(is_active=True).prefetch_related(
        'authors', 'categories', 'images', 'attributes', 'sellers__seller'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'short_description', 'authors__name']
    ordering_fields = ['created_at', 'rating_average', 'quantity_sold', 'list_price']
    pagination_class = CustomPageNumberPagination
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
    
    def get_serializer_class(self):
        if self.action == 'tree':
            return CategoryTreeSerializer
        return CategorySerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Lấy cây thư mục hoàn chỉnh"""
        root_categories = Category.objects.filter(parent=None)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Lấy thư mục con của một thư mục"""
        category = self.get_object()
        children = Category.objects.filter(parent=category)
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """Lấy sách theo thư mục (bao gồm cả thư mục con)"""
        category = self.get_object()
        include_children = request.query_params.get('include_children', 'true').lower() == 'true'
        
        if include_children:
            # Lấy tất cả thư mục con
            child_categories = self._get_all_children(category)
            child_categories.append(category)
            books = Book.objects.filter(
                categories__in=child_categories,
                is_active=True
            ).distinct()
        else:
            # Chỉ lấy sách trong thư mục hiện tại
            books = category.books.filter(is_active=True)
        
        # Áp dụng pagination
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = BookListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)
    
    def _get_all_children(self, category):
        """Lấy tất cả thư mục con (đệ quy)"""
        children = []
        for child in category.category_set.all():
            children.append(child)
            children.extend(self._get_all_children(child))
        return children
    
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
            book = Book.objects.get(id=book_id, is_active=True)
            
            # Kiểm tra tồn kho
            current_in_cart = CartItem.objects.filter(
                cart=cart, book=book
            ).first()
            current_quantity = current_in_cart.quantity if current_in_cart else 0
            total_requested = current_quantity + quantity
            
            if total_requested > book.stock_quantity:
                return Response({
                    'error': f'Chỉ còn {book.stock_quantity} sản phẩm trong kho'
                }, status=400)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, book=book,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)
        except Book.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)
    
    @action(detail=False, methods=['put'], url_path='update/(?P<book_id>[^/.]+)')
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
    
    @action(detail=False, methods=['delete'], url_path='remove/(?P<book_id>[^/.]+)')
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