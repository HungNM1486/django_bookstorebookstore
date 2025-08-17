# Hướng dẫn sử dụng Postman Collection cho Bookstore API

Collection này bao gồm tất cả các API endpoints của hệ thống quản lý sách (Bookstore), được tổ chức theo từng module chức năng.

## 🚀 Cài đặt và thiết lập

### Import Collection

1. Mở Postman
2. Click vào "Import"
3. Chọn file `Bookstore_API_Collection.json`
4. Collection sẽ được import vào workspace


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


**HungNM** 🚀
