# 🐳 Hướng dẫn sử dụng Docker cho Bookstore API

## 📋 Tổng quan

Dự án Bookstore API đã được cấu hình để chạy hoàn toàn bằng Docker, bao gồm:

- **Django Web Server** (Python 3.11)
- **PostgreSQL Database** (PostgreSQL 15)
- **Docker Compose** để quản lý các services

## 🚀 Cài đặt và thiết lập

### 1. Cài đặt Docker

#### Ubuntu/Debian:

```bash
# Cập nhật package list
sudo apt update

# Cài đặt Docker
sudo apt install -y docker.io docker-compose

# Thêm user vào docker group (để không cần sudo)
sudo usermod -aG docker $USER

# Khởi động Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Logout và login lại để áp dụng group changes
```

#### Windows/macOS:

- Tải và cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2. Kiểm tra cài đặt

```bash
# Kiểm tra Docker version
docker --version

# Kiểm tra Docker Compose version
docker-compose --version

# Kiểm tra Docker service
sudo systemctl status docker
```

## 🏃‍♂️ Chạy dự án

### 1. Build và chạy containers

```bash
# Di chuyển vào thư mục dự án
cd /path/to/bookstore

# Build và chạy containers trong background
docker-compose up --build -d

# Hoặc chạy và xem logs
docker-compose up --build
```

### 2. Kiểm tra trạng thái

```bash
# Xem trạng thái các containers
docker-compose ps

# Xem logs của web service
docker-compose logs web

# Xem logs của database service
docker-compose logs db
```

### 3. Chạy migrations và import dữ liệu

```bash
# Chạy migrations
docker-compose exec web python manage.py migrate

# Import dữ liệu mẫu
docker-compose exec web python manage.py import_books data.json

# Tạo superuser (admin)
docker-compose exec web python manage.py createsuperuser
```

## 🔧 Các lệnh Docker hữu ích

### Quản lý containers:

```bash
# Dừng tất cả containers
docker-compose down

# Dừng và xóa volumes (database data)
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild containers
docker-compose build --no-cache
```

### Truy cập container:

```bash
# Truy cập shell của web container
docker-compose exec web bash

# Truy cập PostgreSQL
docker-compose exec db psql -U postgres -d bookstore_db

# Xem logs real-time
docker-compose logs -f web
```

### Quản lý database:

```bash
# Backup database
docker-compose exec db pg_dump -U postgres bookstore_db > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres bookstore_db < backup.sql

# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py import_books data.json
```

## 🌐 Truy cập ứng dụng

### API Endpoints:

- **Base URL**: `http://localhost:8000/api`
- **Admin Interface**: `http://localhost:8000/admin`
- **API Documentation**: `http://localhost:8000/api/`

### Test API:

```bash
# Test API hoạt động
curl http://localhost:8000/api/books/

# Test với Postman
# Import file: Bookstore_API_Collection.json
# Set environment variable: base_url = http://localhost:8000/api
```

## 📁 Cấu trúc Docker

### docker-compose.yml:

```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    container_name: postgres_db
    environment:
      POSTGRES_DB: bookstore_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    container_name: django_web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:
```

### Dockerfile:

```dockerfile
FROM python:3.11-slim

# Cài gói cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🔍 Troubleshooting

### Lỗi thường gặp:

#### 1. Port đã được sử dụng:

```bash
# Kiểm tra port đang sử dụng
sudo netstat -tulpn | grep :8000

# Kill process sử dụng port
sudo kill -9 <PID>

# Hoặc thay đổi port trong docker-compose.yml
ports:
  - "8001:8000"  # Thay đổi từ 8000 thành 8001
```

#### 2. Permission denied:

```bash
# Thêm user vào docker group
sudo usermod -aG docker $USER

# Logout và login lại
# Hoặc chạy với sudo
sudo docker-compose up -d
```

#### 3. Database connection error:

```bash
# Kiểm tra database container
docker-compose ps db

# Restart database
docker-compose restart db

# Kiểm tra logs
docker-compose logs db
```

#### 4. Django migrations error:

```bash
# Xóa migrations và tạo lại
docker-compose exec web python manage.py makemigrations --empty books
docker-compose exec web python manage.py migrate

# Hoặc reset hoàn toàn
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Debug mode:

```bash
# Chạy với debug logs
docker-compose up --build

# Xem logs chi tiết
docker-compose logs -f web

# Truy cập container để debug
docker-compose exec web bash
```

## 📊 Monitoring

### Kiểm tra tài nguyên:

```bash
# Xem tài nguyên containers
docker stats

# Xem disk usage
docker system df

# Cleanup unused resources
docker system prune
```

### Health checks:

```bash
# Kiểm tra API health
curl http://localhost:8000/api/books/

# Kiểm tra database
docker-compose exec db pg_isready -U postgres
```

## 🚀 Production Deployment

### Environment variables:

Tạo file `.env`:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://postgres:password@db:5432/bookstore_db
```

### Production settings:

```bash
# Build production image
docker build -t bookstore:prod .

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Lưu ý quan trọng

### Security:

- ✅ Đổi password database trong production
- ✅ Sử dụng environment variables cho sensitive data
- ✅ Enable HTTPS trong production
- ✅ Cấu hình CORS đúng cách

### Performance:

- ✅ Sử dụng nginx làm reverse proxy
- ✅ Enable database connection pooling
- ✅ Cấu hình caching (Redis)
- ✅ Optimize Docker images

### Backup:

- ✅ Backup database định kỳ
- ✅ Backup source code
- ✅ Test restore procedure

---

## 🎯 Quick Start Commands

```bash
# 1. Clone repository
git clone <repository-url>
cd bookstore

# 2. Chạy dự án
docker-compose up --build -d

# 3. Setup database
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py import_books data.json
docker-compose exec web python manage.py createsuperuser

# 4. Test API
curl http://localhost:8000/api/books/

# 5. Import Postman collection
# File: Bookstore_API_Collection.json
# Environment: base_url = http://localhost:8000/api
```

**🎉 Chúc bạn thành công với Docker setup!**
