from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .admin_views import *
from .upload_views import *

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'books', BookViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'users', UserViewSet)
router.register(r'authors', AuthorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# Legacy endpoints mapping for existing frontend
urlpatterns += [
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('register/', AuthViewSet.as_view({'post': 'register'}), name='register'),
    path('profile/', AuthViewSet.as_view({'get': 'profile'}), name='profile'),
    path('logout/', AuthViewSet.as_view({'post': 'logout'}), name='logout'),
]

# Admin APIs
urlpatterns += [
    # Dashboard APIs
    path('admin/dashboard/stats/', dashboard_stats, name='admin_dashboard_stats'),
    path('admin/dashboard/revenue/', dashboard_revenue, name='admin_dashboard_revenue'),
    path('admin/dashboard/orders/', dashboard_orders, name='admin_dashboard_orders'),
    
    # CRUD APIs cho Books
    path('admin/books/', create_book, name='admin_create_book'),
    path('admin/books/<str:book_id>/', update_book, name='admin_update_book'),
    path('admin/books/<str:book_id>/delete/', delete_book, name='admin_delete_book'),
    
    # CRUD APIs cho Categories
    path('admin/categories/', create_category, name='admin_create_category'),
    path('admin/categories/<str:category_id>/', update_category, name='admin_update_category'),
    path('admin/categories/<str:category_id>/delete/', delete_category, name='admin_delete_category'),
    
    # CRUD APIs cho Orders
    path('admin/orders/<str:order_id>/status/', update_order_status, name='admin_update_order_status'),
    path('admin/orders/', admin_orders, name='admin_orders'),
    
    # Admin Users
    path('admin/users/', admin_users, name='admin_users'),
    
    # Upload APIs
    path('admin/upload/image/', upload_image, name='admin_upload_image'),
    path('admin/upload/cover/', upload_cover, name='admin_upload_cover'),
    path('admin/upload/multiple/', upload_multiple_images, name='admin_upload_multiple'),
    path('admin/upload/delete/', delete_image, name='admin_delete_image'),
]