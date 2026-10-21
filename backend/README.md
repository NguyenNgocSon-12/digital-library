# Backend · Spring Boot

Ứng dụng Maven dùng Java 17+, Spring Boot, Spring Web MVC, Spring Data MongoDB, Spring Data Redis và Validation.

```bash
cd backend
./mvnw spring-boot:run
# hoặc: mvn spring-boot:run
curl http://localhost:8080/api/health
```

MongoDB và Redis chạy bằng `docker compose up -d` ở thư mục gốc. Cấu hình mặc định trong `application.yml` khớp Docker Compose; có thể ghi đè bằng `MONGO_URI`, `REDIS_URL`, `SERVER_PORT`. Không đưa mật khẩu thật vào Git.

| Package | Người phụ trách | Nhiệm vụ |
|---|---|---|
| `catalog` | Vũ | Sách, chương, tìm kiếm, MongoDB |
| `identity` | Vũ | Độc giả, đăng ký/đăng nhập, MongoDB |
| `reading` | Đạt | Tiến trình đọc, Redis Hash |
| `ranking` | Đạt | Lượt đọc, Top sách, Redis ZSET |
| `common` | Cả nhóm | Cấu hình và kiểu dữ liệu dùng chung |

Khung hiện chỉ có endpoint `GET /api/health`. Các endpoint nghiệp vụ được phân công trong [docs/SHARED.md](../docs/SHARED.md).
