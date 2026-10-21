# 👤 Vũ – SV1: Data Architect & CRUD Lead

**Phạm vi code:** `backend/src/mongo/`, `docs/ARCHITECTURE.md`

## Phase 1
### A. Thiết kế & báo cáo (2.5đ – barem mục 1)
- [ ] Giải trình kiến trúc Polyglot Persistence (1.0đ) trong `docs/ARCHITECTURE.md`
- [ ] Thiết kế JSON Schema MongoDB: `books` (chương, mục lồng nhau), `users` (+ validator, index)
- [ ] Thiết kế cấu trúc Redis Hashes / ZSET (phối hợp Đạt chốt quy ước key)
- [ ] Vẽ sơ đồ kiến trúc & document model

### B. API CRUD trên MongoDB (2.5đ – barem mục 2)
- [ ] Khởi tạo backend (Express), kết nối MongoDB
- [ ] CRUD **sách**: tạo / danh sách (phân trang, lọc thể loại) / chi tiết / sửa / xóa
- [ ] **Thêm chương mới** vào sách (`$push`), sửa/xóa chương
- [ ] Quản lý **tài khoản độc giả**: đăng ký, đăng nhập, xem/sửa/xóa
- [ ] Tạo index (text index tiêu đề/tác giả, index thể loại)
- [ ] Viết tài liệu API (danh sách endpoint, ví dụ request/response)

## Phase 2
- [ ] Hỗ trợ Đạt/Sơn: API lấy nội dung chương (`bookId` + `chapterNo`), lấy thông tin sách cho BXH
- [ ] Bổ sung báo cáo: kết quả đo hiệu năng, bảng so sánh Mongo vs Redis
- [ ] Hoàn thiện báo cáo cuối, rà soát barem
- [ ] Tham gia demo: đọc đến trang 30 rồi đóng trình duyệt

## Definition of Done
- Mọi endpoint CRUD test được qua Postman/curl; dữ liệu hiển thị đúng trong Compass.
- Báo cáo đủ 2 phần: giải trình + thiết kế (2.5đ).
