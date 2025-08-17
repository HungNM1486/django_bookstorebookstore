from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'username']
    ordering = ['-created_at']

class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1

class BookAttributeInline(admin.TabularInline):
    model = BookAttribute
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'list_price', 'rating_average', 'quantity_sold', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'created_at', 'categories']
    search_fields = ['title', 'description', 'authors__name']
    filter_horizontal = ['authors', 'categories']
    inlines = [BookImageInline, BookAttributeInline]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_leaf', 'parent']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['customer_name', 'customer_email']
    readonly_fields = ['created_at', 'updated_at']