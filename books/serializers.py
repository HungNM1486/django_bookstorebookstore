# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'slug']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_leaf']

class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ['base_url', 'large_url', 'medium_url', 'small_url', 'thumbnail_url', 'is_gallery', 'position', 'label']

class BookAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAttribute
        fields = ['code', 'name', 'value']

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['id', 'name', 'logo', 'link', 'store_id', 'is_best_store']

class BookSellerSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    
    class Meta:
        model = BookSeller
        fields = ['sku', 'price', 'seller']

class BookListSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    categories = CategorySerializer(read_only=True)
    images = BookImageSerializer(many=True, read_only=True)
    quantity_sold = serializers.SerializerMethodField()
    current_seller = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'short_description',
            'list_price', 'original_price', 'rating_average',
            'quantity_sold', 'book_cover', 'authors', 'categories',
            'images', 'current_seller', 'is_featured'
        ]
    
    def get_quantity_sold(self, obj):
        return {
            'text': obj.quantity_sold_text or f'Đã bán {obj.quantity_sold}',
            'value': obj.quantity_sold
        }
    
    def get_current_seller(self, obj):
        current_seller = obj.sellers.filter(is_current=True).first()
        if current_seller:
            return {
                'id': current_seller.seller.id,
                'sku': current_seller.sku,
                'name': current_seller.seller.name,
                'link': current_seller.seller.link,
                'logo': current_seller.seller.logo,
                'price': current_seller.price,
                'store_id': current_seller.seller.store_id,
                'is_best_store': current_seller.seller.is_best_store
            }
        return None

class BookDetailSerializer(BookListSerializer):
    attributes = BookAttributeSerializer(many=True, read_only=True)
    sellers = BookSellerSerializer(many=True, read_only=True)
    
    class Meta(BookListSerializer.Meta):
        fields = BookListSerializer.Meta.fields + ['attributes', 'sellers']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'confirm_password', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        return attrs

class CartItemSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    book_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'book', 'book_id', 'quantity', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_amount', 'total_items', 'created_at', 'updated_at']
    
    def get_total_amount(self, obj):
        return sum(item.quantity * item.book.list_price for item in obj.items.all())
    
    def get_total_items(self, obj):
        return obj.items.count()

class OrderItemSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity', 'price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'total_amount', 'shipping_fee', 'discount_amount',
            'status', 'payment_method', 'shipping_method',
            'customer_name', 'customer_email', 'customer_phone', 'shipping_address',
            'notes', 'item_count', 'items', 'created_at', 'updated_at'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'payment_method', 'shipping_method', 'customer_name',
            'customer_email', 'customer_phone', 'shipping_address',
            'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Calculate total
        total = 0
        for item_data in items_data:
            book = Book.objects.get(id=item_data['book_id'])
            total += item_data['quantity'] * book.list_price
        
        validated_data['user'] = user
        validated_data['total_amount'] = total
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            book = Book.objects.get(id=item_data['book_id'])
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=item_data['quantity'],
                price=book.list_price
            )
        
        return order