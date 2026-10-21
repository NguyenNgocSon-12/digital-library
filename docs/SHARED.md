# Phần dùng chung và hợp đồng tích hợp

Tài liệu này là điểm thống nhất giữa backend Spring Boot, frontend React và script seed. **Khung hiện chỉ triển khai `GET /api/health`**. Các endpoint bên dưới là hợp đồng dự kiến để từng thành viên hiện thực; khi đổi tên trường hoặc đường dẫn, sửa tài liệu này trong cùng Pull Request.

## 1. Ranh giới sở hữu

| Khu vực | Phụ trách chính | Nội dung |
|---|---|---|
| `backend/src/main/java/vn/edu/huit/digitallibrary/catalog/` | Vũ | Sách, chương, tìm kiếm, CRUD MongoDB |
| `backend/src/main/java/vn/edu/huit/digitallibrary/identity/` | Vũ | Độc giả, đăng ký, đăng nhập, MongoDB |
| `backend/src/main/java/vn/edu/huit/digitallibrary/reading/` | Đạt | Tiến trình đọc trong Redis Hash |
| `backend/src/main/java/vn/edu/huit/digitallibrary/ranking/` | Đạt | Lượt đọc và bảng xếp hạng Redis ZSET |
| `frontend/src/features/` | Sơn | Giao diện catalog, identity, reading, ranking |
| `scripts/seed/` | Sơn, phối hợp Đạt | Seed MongoDB rồi Redis bằng bookId thật |
| `backend/.../common/`, `frontend/src/shared/`, cấu hình gốc | Cả nhóm | Dùng chung; mô tả thay đổi trong PR và báo hai người còn lại |

Trong mỗi domain backend có thể tạo `controller/`, `service/`, `repository/`, `model/`, `dto/` khi cần. Domain chỉ gọi domain khác qua service công khai hoặc DTO; không truy cập trực tiếp repository của domain khác. Đặc biệt, ranking chỉ lưu `bookId` trong Redis, không sao chép document sách.

## 2. Quy ước dữ liệu

- ID sách và độc giả là chuỗi MongoDB ObjectId trong JSON. Dùng nhất quán `bookId`, `userId`.
- Sách MongoDB: `id, title, author, categories[], description, coverUrl, chapters[]`. Mỗi chương có `chapterNo, title, content, sections[]`; số chương bắt đầu từ 1.
- Tiến trình Redis: key `progress:{userId}:{bookId}`, Hash gồm `chapter, page, line, updatedAt`. `chapter` và `page` bắt đầu từ 1, `line` bắt đầu từ 0. `updatedAt` theo ISO 8601 UTC. Chưa đặt TTL trong bản demo.
- Xếp hạng Redis: key `ranking:books`, ZSET với member là `bookId`, score là lượt mở chương. Chỉ tăng một lần cho mỗi lần mở chương theo quy tắc nhóm chốt khi triển khai.
- Không đưa `passwordHash` ra response. Cơ chế xác thực và phân quyền cần được Vũ chốt trước khi Sơn nối biểu mẫu; không giả định `userId` gửi từ trình duyệt là bằng chứng đăng nhập.

## 3. API dự kiến

Tất cả endpoint nghiệp vụ dùng tiền tố `/api` và JSON. Lỗi chuẩn dự kiến: `{ "code": "NOT_FOUND", "message": "..." }`; `404` khi thiếu tài nguyên, `400` khi dữ liệu không hợp lệ.

| Nhóm | Endpoint | Người làm | Ghi chú |
|---|---|---|---|
| Chung | `GET /api/health` | Khung chung | Đã có, trả `{"status":"ok"}` |
| Sách | `GET /api/books?page=0&size=20&category=...` | Vũ | Phân trang, lọc thể loại |
| Sách | `GET /api/books/{bookId}` | Vũ | Chi tiết và chương |
| Sách | `POST /api/books`, `PUT /api/books/{bookId}`, `DELETE /api/books/{bookId}` | Vũ | CRUD; giới hạn quyền quản trị sau khi có auth |
| Chương | `POST /api/books/{bookId}/chapters`, `PUT /api/books/{bookId}/chapters/{chapterNo}`, `DELETE /api/books/{bookId}/chapters/{chapterNo}` | Vũ | Chương lồng trong document sách |
| Độc giả | `POST /api/users`, `POST /api/auth/login`, `GET/PUT/DELETE /api/users/{userId}` | Vũ | Chốt request/response và auth trước tích hợp |
| Tiến trình | `GET /api/progress/{userId}/{bookId}`, `PUT /api/progress/{userId}/{bookId}` | Đạt | Body PUT: `{"chapter":1,"page":1,"line":0}` |
| Lượt đọc | `POST /api/books/{bookId}/read` | Đạt | Tăng score khi mở chương |
| Xếp hạng | `GET /api/ranking?top=10` | Đạt | Trả `[{ "bookId": "...", "score": 42 }]`; Sơn ghép sách từ API catalog |

Vũ và Đạt nên đưa ví dụ response thật vào đây khi endpoint hoàn thành. Nếu endpoint trả DTO khác dự kiến, cập nhật bảng trước khi Sơn nối giao diện.

## 4. Chạy và tích hợp

1. Ở thư mục gốc, chạy `cp .env.example .env && docker compose up -d`.
2. Chạy backend: `cd backend && ./mvnw spring-boot:run` (cần Java 17+).
3. Chạy frontend: `cd frontend && npm install && npm run dev` (Node theo yêu cầu Vite).
4. Truy cập `http://localhost:5173`; Vite proxy `/api` đến `http://localhost:8080`. Kiểm tra `curl http://localhost:8080/api/health`.

Spring Boot dùng `MONGO_URI`, `REDIS_URL`, `SERVER_PORT` nếu được export vào môi trường; mặc định khớp Docker Compose cho máy local. `.env` chỉ được Docker Compose tự đọc, Spring Boot không tự nạp file này. Khi đổi cổng backend, cập nhật proxy trong `frontend/vite.config.js`.

## 5. Thứ tự tích hợp

1. Vũ chốt schema sách và DTO API, cung cấp CRUD cơ bản.
2. Sơn seed MongoDB bằng ID ổn định hoặc ghi nhận các `bookId` vừa tạo; Đạt seed Redis từ đúng các ID này.
3. Đạt hoàn thành progress và ranking; Sơn nối E-Reader và Top sách.
4. Vũ chốt auth trước khi gắn thao tác quản trị hoặc tiến trình đọc với người dùng thật.

Mỗi PR chỉ sửa domain mình phụ trách. Khi phải sửa file dùng chung, ghi rõ lý do, ảnh hưởng tới domain còn lại và cập nhật ví dụ request/response tại đây.
