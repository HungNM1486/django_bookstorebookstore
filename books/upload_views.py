import os
import uuid
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request):
    """Upload ảnh sách"""
    if 'image' not in request.FILES:
        return Response(
            {'error': 'Không tìm thấy file ảnh'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = request.FILES['image']
    
    # Kiểm tra loại file
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        return Response(
            {'error': 'Chỉ chấp nhận file ảnh (JPEG, PNG, WebP)'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Kiểm tra kích thước file (max 5MB)
    if image_file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'File ảnh không được lớn hơn 5MB'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Tạo tên file unique
    file_extension = os.path.splitext(image_file.name)[1]
    unique_filename = f"book_images/{uuid.uuid4()}{file_extension}"
    
    try:
        # Lưu file
        path = default_storage.save(unique_filename, ContentFile(image_file.read()))
        url = default_storage.url(path)
        
        return Response({
            'success': True,
            'url': url,
            'filename': unique_filename,
            'size': image_file.size
        })
    except Exception as e:
        return Response(
            {'error': f'Lỗi khi upload file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def upload_cover(request):
    """Upload ảnh bìa sách"""
    if 'cover' not in request.FILES:
        return Response(
            {'error': 'Không tìm thấy file ảnh bìa'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cover_file = request.FILES['cover']
    
    # Kiểm tra loại file
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if cover_file.content_type not in allowed_types:
        return Response(
            {'error': 'Chỉ chấp nhận file ảnh (JPEG, PNG, WebP)'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Kiểm tra kích thước file (max 3MB cho ảnh bìa)
    if cover_file.size > 3 * 1024 * 1024:
        return Response(
            {'error': 'File ảnh bìa không được lớn hơn 3MB'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Tạo tên file unique
    file_extension = os.path.splitext(cover_file.name)[1]
    unique_filename = f"book_covers/{uuid.uuid4()}{file_extension}"
    
    try:
        # Lưu file
        path = default_storage.save(unique_filename, ContentFile(cover_file.read()))
        url = default_storage.url(path)
        
        return Response({
            'success': True,
            'url': url,
            'filename': unique_filename,
            'size': cover_file.size
        })
    except Exception as e:
        return Response(
            {'error': f'Lỗi khi upload file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def upload_multiple_images(request):
    """Upload nhiều ảnh cùng lúc"""
    if 'images' not in request.FILES:
        return Response(
            {'error': 'Không tìm thấy file ảnh'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_files = request.FILES.getlist('images')
    
    if len(image_files) > 10:
        return Response(
            {'error': 'Chỉ được upload tối đa 10 ảnh cùng lúc'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uploaded_files = []
    errors = []
    
    for i, image_file in enumerate(image_files):
        # Kiểm tra loại file
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_types:
            errors.append(f'File {i+1}: Chỉ chấp nhận file ảnh (JPEG, PNG, WebP)')
            continue
        
        # Kiểm tra kích thước file (max 5MB)
        if image_file.size > 5 * 1024 * 1024:
            errors.append(f'File {i+1}: File ảnh không được lớn hơn 5MB')
            continue
        
        # Tạo tên file unique
        file_extension = os.path.splitext(image_file.name)[1]
        unique_filename = f"book_images/{uuid.uuid4()}{file_extension}"
        
        try:
            # Lưu file
            path = default_storage.save(unique_filename, ContentFile(image_file.read()))
            url = default_storage.url(path)
            
            uploaded_files.append({
                'url': url,
                'filename': unique_filename,
                'size': image_file.size,
                'original_name': image_file.name
            })
        except Exception as e:
            errors.append(f'File {i+1}: Lỗi khi upload - {str(e)}')
    
    return Response({
        'success': len(uploaded_files) > 0,
        'uploaded_files': uploaded_files,
        'errors': errors,
        'total_uploaded': len(uploaded_files),
        'total_errors': len(errors)
    })


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_image(request):
    """Xóa ảnh"""
    filename = request.data.get('filename')
    
    if not filename:
        return Response(
            {'error': 'Thiếu tên file cần xóa'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Kiểm tra file có tồn tại không
        if default_storage.exists(filename):
            default_storage.delete(filename)
            return Response({
                'success': True,
                'message': 'Đã xóa file thành công'
            })
        else:
            return Response(
                {'error': 'File không tồn tại'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    except Exception as e:
        return Response(
            {'error': f'Lỗi khi xóa file: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
