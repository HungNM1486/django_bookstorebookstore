from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

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
]