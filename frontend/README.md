# Frontend · React

Giao diện React dùng Vite. Khung hiện có các màn hình theo domain và chỉ gọi `GET /api/health` để kiểm tra kết nối backend; các màn hình nghiệp vụ là điểm bắt đầu để Sơn triển khai.

```bash
cd frontend
npm install
npm run dev
```

Mở địa chỉ Vite in ra ở terminal (mặc định `http://localhost:5173`). Vite chuyển tiếp `/api/*` đến Spring Boot ở `http://localhost:8080`.

- `src/features/catalog`: kho sách và quản trị.
- `src/features/identity`: đăng ký/đăng nhập.
- `src/features/reading`: E-Reader.
- `src/features/ranking`: bảng xếp hạng.
- `src/shared`: API client và thành phần dùng chung.

Xem [hợp đồng tích hợp](../docs/SHARED.md) trước khi nối API.
