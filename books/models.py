from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    is_leaf = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.TextField(blank=True)
    
    # Pricing
    list_price = models.DecimalField(max_digits=12, decimal_places=0)
    original_price = models.DecimalField(max_digits=12, decimal_places=0)
    
    # Stats
    rating_average = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], 
        default=0
    )
    quantity_sold = models.IntegerField(default=0)
    quantity_sold_text = models.CharField(max_length=100, blank=True)
    
    # Book details
    book_cover = models.CharField(max_length=100, blank=True)  # Bìa cứng/mềm
    
    # Relationships
    authors = models.ManyToManyField(Author, related_name='books')
    categories = models.ManyToManyField(Category, related_name='books')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class BookImage(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    base_url = models.URLField()
    large_url = models.URLField()
    medium_url = models.URLField()
    small_url = models.URLField()
    thumbnail_url = models.URLField()
    is_gallery = models.BooleanField(default=True)
    position = models.IntegerField(null=True, blank=True)
    label = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['position']

class BookAttribute(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='attributes')
    code = models.CharField(max_length=100)  # publisher, number_of_page, etc.
    name = models.CharField(max_length=255)
    value = models.TextField()
    
    class Meta:
        unique_together = ['book', 'code']

class Seller(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.URLField(blank=True)
    link = models.URLField(blank=True)
    store_id = models.IntegerField(unique=True)
    is_best_store = models.BooleanField(default=False)
    is_offline_installment_supported = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class BookSeller(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='sellers')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['book', 'seller']

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'book']

class Order(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
    ]
    
    PAYMENT_CHOICES = [
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('credit_card', 'Thẻ tín dụng'),
        ('wallet', 'Ví điện tử'),
    ]
    
    SHIPPING_CHOICES = [
        ('standard', 'Giao hàng tiêu chuẩn'),
        ('express', 'Giao hàng nhanh'),
        ('same_day', 'Giao trong ngày'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    
    # Status and methods
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_CHOICES)
    
    # Customer info
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def item_count(self):
        return self.items.count()

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=0)  # Price at time of order
    
    @property
    def total_price(self):
        return self.quantity * self.price