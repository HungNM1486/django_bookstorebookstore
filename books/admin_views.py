from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Book, Order, User, Category
from .serializers import BookListSerializer, CategorySerializer, OrderSerializer, UserSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """Thống kê tổng quan cho admin dashboard"""
    
    # Thống kê tổng quan
    total_books = Book.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_categories = Category.objects.count()
    
    # Đơn hàng theo trạng thái
    orders_by_status = Order.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Doanh thu tháng này
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_revenue = Order.objects.filter(
        created_at__month=current_month,
        created_at__year=current_year,
        status__in=['confirmed', 'shipping', 'delivered']
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Đơn hàng gần đây (7 ngày qua)
    recent_orders = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Sách bán chạy nhất (top 5)
    top_books = Book.objects.order_by('-quantity_sold')[:5]
    
    return Response({
        'overview': {
            'total_books': total_books,
            'total_orders': total_orders,
            'total_users': total_users,
            'total_categories': total_categories,
            'monthly_revenue': monthly_revenue,
            'recent_orders': recent_orders
        },
        'orders_by_status': list(orders_by_status),
        'top_books': BookListSerializer(top_books, many=True).data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_revenue(request):
    """Thống kê doanh thu"""
    
    # Doanh thu theo tháng (6 tháng gần đây)
    months = []
    revenues = []
    
    for i in range(6):
        date = timezone.now() - timedelta(days=30*i)
        month_revenue = Order.objects.filter(
            created_at__month=date.month,
            created_at__year=date.year,
            status__in=['confirmed', 'shipping', 'delivered']
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        months.append(f"{date.month}/{date.year}")
        revenues.append(month_revenue)
    
    # Doanh thu theo ngày (7 ngày gần đây)
    daily_revenues = []
    daily_dates = []
    
    for i in range(7):
        date = timezone.now() - timedelta(days=i)
        daily_revenue = Order.objects.filter(
            created_at__date=date.date(),
            status__in=['confirmed', 'shipping', 'delivered']
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        daily_revenues.append(daily_revenue)
        daily_dates.append(date.strftime('%d/%m'))
    
    return Response({
        'monthly_revenue': {
            'months': months[::-1],  # Đảo ngược để hiển thị từ cũ đến mới
            'revenues': revenues[::-1]
        },
        'daily_revenue': {
            'dates': daily_dates[::-1],
            'revenues': daily_revenues[::-1]
        }
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_orders(request):
    """Thống kê đơn hàng gần đây"""
    
    # Đơn hàng gần đây (10 đơn hàng mới nhất)
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Đơn hàng theo trạng thái
    pending_orders = Order.objects.filter(status='confirmed').count()
    shipping_orders = Order.objects.filter(status='shipping').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    return Response({
        'recent_orders': OrderSerializer(recent_orders, many=True).data,
        'orders_summary': {
            'pending': pending_orders,
            'shipping': shipping_orders,
            'delivered': delivered_orders,
            'cancelled': cancelled_orders
        }
    })


# CRUD APIs cho Books
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_book(request):
    """Tạo sách mới"""
    serializer = BookListSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_book(request, book_id):
    """Cập nhật sách"""
    try:
        book = Book.objects.get(id=book_id)
        serializer = BookListSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Book.DoesNotExist:
        return Response({'error': 'Sách không tồn tại'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_book(request, book_id):
    """Xóa sách"""
    try:
        book = Book.objects.get(id=book_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Book.DoesNotExist:
        return Response({'error': 'Sách không tồn tại'}, status=status.HTTP_404_NOT_FOUND)


# CRUD APIs cho Categories
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_category(request):
    """Tạo danh mục mới"""
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_category(request, category_id):
    """Cập nhật danh mục"""
    try:
        category = Category.objects.get(id=category_id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Category.DoesNotExist:
        return Response({'error': 'Danh mục không tồn tại'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_category(request, category_id):
    """Xóa danh mục"""
    try:
        category = Category.objects.get(id=category_id)
        # Kiểm tra xem có sách nào trong danh mục không
        if category.books.exists():
            return Response(
                {'error': 'Không thể xóa danh mục có sách'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response({'error': 'Danh mục không tồn tại'}, status=status.HTTP_404_NOT_FOUND)


# CRUD APIs cho Orders
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_order_status(request, order_id):
    """Cập nhật trạng thái đơn hàng"""
    try:
        order = Order.objects.get(id=order_id)
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Trạng thái không hợp lệ'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cập nhật trạng thái
        order.status = new_status
        
        # Cập nhật thời gian nếu cần
        if new_status == 'shipping' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
        
        order.save()
        return Response(OrderSerializer(order).data)
    except Order.DoesNotExist:
        return Response({'error': 'Đơn hàng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders(request):
    """Lấy danh sách đơn hàng cho admin (tất cả đơn hàng)"""
    orders = Order.objects.select_related('user').prefetch_related('items__book').order_by('-created_at')
    
    # Filter theo trạng thái
    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Search theo customer name hoặc email
    search = request.query_params.get('search')
    if search:
        orders = orders.filter(
            Q(customer_name__icontains=search) | 
            Q(customer_email__icontains=search)
        )
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_orders = orders.count()
    orders_page = orders[start:end]
    
    return Response({
        'orders': OrderSerializer(orders_page, many=True).data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total_orders,
            'total_pages': (total_orders + page_size - 1) // page_size
        }
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users(request):
    """Lấy danh sách users cho admin"""
    users = User.objects.all().order_by('-created_at')
    
    # Filter theo role
    role_filter = request.query_params.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Search theo email hoặc username
    search = request.query_params.get('search')
    if search:
        users = users.filter(
            Q(email__icontains=search) | 
            Q(username__icontains=search)
        )
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_users = users.count()
    users_page = users[start:end]
    
    return Response({
        'users': UserSerializer(users_page, many=True).data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total_users,
            'total_pages': (total_users + page_size - 1) // page_size
        }
    })
