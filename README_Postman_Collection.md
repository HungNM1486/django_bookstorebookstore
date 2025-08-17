# Hướng dẫn sử dụng Postman Collection cho Bookstore API

## 📋 Tổng quan

Collection này bao gồm tất cả các API endpoints của hệ thống quản lý sách (Bookstore), được tổ chức theo từng module chức năng.

## 🚀 Cài đặt và thiết lập

### 1. Import Collection

1. Mở Postman
2. Click vào "Import"
3. Chọn file `Bookstore_API_Collection.json`
4. Collection sẽ được import vào workspace

### 2. Thiết lập Environment Variables

Tạo một environment mới với các biến sau:

| Variable             | Giá trị mặc định        | Mô tả               |
| -------------------- | ----------------------- | ------------------- |
| `base_url`           | `http://localhost:8000` | URL cơ sở của API   |
| `access_token`       | (để trống)              | JWT access token    |
| `refresh_token`      | (để trống)              | JWT refresh token   |
| `admin_access_token` | (để trống)              | Token của admin     |
| `book_id`            | (để trống)              | ID của sách để test |
| `category_id`        | (để trống)              | ID của danh mục     |
| `author_id`          | (để trống)              | ID của tác giả      |
| `order_id`           | (để trống)              | ID của đơn hàng     |
| `user_id`            | (để trống)              | ID của user         |

## 🔐 Authentication

### Quy trình xác thực:

1. **Đăng ký tài khoản** → Nhận thông tin user
2. **Đăng nhập** → Nhận access_token và refresh_token
3. **Sử dụng access_token** trong header `Authorization: Bearer {token}`
4. **Đăng xuất** → Blacklist refresh_token

### Lưu ý:

- Access token có thời hạn 60 phút
- Refresh token có thời hạn 7 ngày
- Collection tự động lưu token sau khi đăng nhập thành công

## 📚 Các Module API

### 1. Authentication

- **POST** `/auth/register/` - Đăng ký tài khoản mới
- **POST** `/auth/login/` - Đăng nhập
- **GET** `/auth/profile/` - Xem thông tin profile
- **POST** `/auth/logout/` - Đăng xuất

### 2. Books

- **GET** `/books/` - Lấy danh sách sách (có phân trang)
- **GET** `/books/?search={keyword}` - Tìm kiếm sách
- **GET** `/books/?categories__id={id}` - Lọc theo danh mục
- **GET** `/books/?ordering={field}` - Sắp xếp
- **GET** `/books/featured/` - Sách nổi bật
- **GET** `/books/{id}/` - Chi tiết sách
- **GET** `/books/{id}/similar/` - Sách tương tự

### 3. Categories

- **GET** `/categories/` - Danh sách danh mục
- **GET** `/categories/{id}/` - Chi tiết danh mục

### 4. Authors

- **GET** `/authors/` - Danh sách tác giả
- **GET** `/authors/{id}/` - Chi tiết tác giả

### 5. Cart

- **GET** `/carts/cart_items/` - Xem giỏ hàng
- **POST** `/carts/add/` - Thêm sách vào giỏ
- **PUT** `/carts/{book_id}/` - Cập nhật số lượng
- **DELETE** `/carts/{book_id}/` - Xóa sách khỏi giỏ
- **DELETE** `/carts/clear/` - Xóa toàn bộ giỏ hàng

### 6. Orders

- **GET** `/orders/` - Danh sách đơn hàng
- **POST** `/orders/` - Tạo đơn hàng mới
- **GET** `/orders/{id}/` - Chi tiết đơn hàng
- **POST** `/orders/{id}/cancel/` - Hủy đơn hàng

### 7. Users (Admin only)

- **GET** `/users/` - Danh sách users
- **GET** `/users/{id}/` - Chi tiết user

## 🔍 Cách sử dụng

### Bước 1: Khởi tạo dữ liệu test

```bash
# Chạy server Django
python manage.py runserver

# Import dữ liệu mẫu (nếu có)
python manage.py import_books
```

### Bước 2: Test Authentication

1. Chạy request "Đăng ký tài khoản"
2. Chạy request "Đăng nhập" → Token sẽ tự động được lưu
3. Test request "Xem thông tin profile"

### Bước 3: Test Books API

1. Lấy danh sách sách để có `book_id`
2. Cập nhật biến `book_id` trong environment
3. Test các API khác với book_id

### Bước 4: Test Cart & Orders

1. Thêm sách vào giỏ hàng
2. Xem giỏ hàng
3. Tạo đơn hàng
4. Xem chi tiết đơn hàng

## 📝 Ví dụ Request/Response

### Đăng nhập

**Request:**

```json
POST /auth/login/
{
    "email": "test@example.com",
    "password": "testpass123"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid-here",
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Nguyễn",
    "last_name": "Văn A"
  }
}
```

### Lấy danh sách sách

**Request:**

```json
GET /books/?page=1&page_size=10&search=harry&ordering=-rating_average
```

**Response:**

```json
{
  "count": 100,
  "next": "http://localhost:8000/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "title": "Harry Potter and the Philosopher's Stone",
      "slug": "harry-potter-philosophers-stone",
      "list_price": "150000",
      "rating_average": 4.5,
      "quantity_sold": 1000
    }
  ]
}
```

## ⚠️ Lưu ý quan trọng

### Permissions

- **Public APIs**: Books, Categories, Authors (không cần token)
- **User APIs**: Cart, Orders, Profile (cần access_token)
- **Admin APIs**: Users (cần admin access_token)

### Error Handling

- **400**: Bad Request - Dữ liệu không hợp lệ
- **401**: Unauthorized - Chưa đăng nhập hoặc token hết hạn
- **403**: Forbidden - Không có quyền truy cập
- **404**: Not Found - Tài nguyên không tồn tại
- **500**: Internal Server Error - Lỗi server

### Rate Limiting

- API có thể có giới hạn số request
- Nếu gặp lỗi 429, hãy đợi một lúc rồi thử lại

## 🛠️ Troubleshooting

### Token hết hạn

```bash
# Lấy token mới bằng refresh token
POST /auth/token/refresh/
{
    "refresh": "your-refresh-token"
}
```

### CORS Issues

Đảm bảo Django settings có CORS_ALLOWED_ORIGINS phù hợp:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Database Issues

```bash
# Kiểm tra migrations
python manage.py showmigrations

# Chạy migrations nếu cần
python manage.py migrate
```

## 📞 Hỗ trợ

Nếu gặp vấn đề khi sử dụng collection này:

1. Kiểm tra server Django có đang chạy không
2. Kiểm tra database connection
3. Xem logs của Django server
4. Kiểm tra environment variables đã được set đúng chưa

---

**Collection được tạo bởi AI Assistant cho Bookstore API** 🚀
