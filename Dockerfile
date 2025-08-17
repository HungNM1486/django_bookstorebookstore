FROM python:3.11-slim

# Cài gói cần thiết để build psycopg2 và các lib khác
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy requirements và cài đặt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . /app/

# Mở port 8000
EXPOSE 8000

# Lệnh mặc định (sẽ override bởi docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
