# 👤 Đạt – SV2: Advanced Query Specialist (Redis)

**Phạm vi code:** `backend/src/redis/`

## Phase 1
- [ ] Cấu hình kết nối Redis (`ioredis`), module dùng chung
- [ ] Cùng Vũ chốt quy ước key (`progress:{userId}:{bookId}`, `ranking:books`)
- [ ] Script seed Redis: **≥ 50 Hash** tiến trình đọc + **1 ZSET 50 cuốn sách** kèm lượt đọc (phối hợp Sơn, dùng `bookId` thật từ Mongo)
- [ ] Thử các lệnh cơ bản trên Redis Insight, ghi lại lệnh mẫu

## Phase 2 (trọng tâm – barem mục 3, 2.5đ)
### A. Lưu tiến trình đọc dở (Redis Hashes)
- [ ] `POST /progress` → `HSET progress:{userId}:{bookId} chapter page line updatedAt`
- [ ] `GET /progress/:userId/:bookId` → `HGETALL`, trả về độ trễ cực thấp
- [ ] (Tùy chọn) `GET /progress/:userId` → danh sách sách đang đọc dở

### B. Bảng xếp hạng sách đọc nhiều nhất (Redis ZSET)
- [ ] `POST /books/:id/read` → `ZINCRBY ranking:books 1 {bookId}` mỗi khi độc giả đọc chương
- [ ] `GET /ranking?top=10` → `ZREVRANGE ranking:books 0 N-1 WITHSCORES`, ghép thông tin sách từ Mongo
- [ ] (Tùy chọn) Chống tăng điểm lặp quá nhanh: khóa `SET NX EX` theo user + chương

### C. Kiểm thử hiệu năng (phối hợp Sơn)
- [ ] Đo độ trễ lấy tiến trình: Redis vs Mongo (ví dụ 1000 lần)
- [ ] Ghi kết quả cho Vũ đưa vào báo cáo

### D. Demo
- [ ] Đọc liên tục một cuốn sách để ZSET tăng điểm, BXH nhảy vị trí

## Definition of Done
- Đóng/mở lại sách → trả về đúng trang đã lưu.
- Redis Insight thấy điểm ZSET tăng theo từng lần đọc.
