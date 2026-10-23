# 👤 Đạt – SV2: Advanced Query Specialist (Redis)

**Phạm vi code:** `backend/src/main/java/vn/edu/huit/digitallibrary/reading/` và `ranking/`. Xem [phần dùng chung](../docs/SHARED.md).

## Phase 1
- [x] Hiện thực Redis bằng Spring Data Redis trên khung Spring Boot đã có — Mongo/Redis thật và regression ID đã qua, [bằng chứng](../docs/dat/ID_NORMALIZATION.md).
- [x] Cùng Vũ chốt quy ước key (`progress:{userId}:{bookId}`, `ranking:books`) — quy ước đã có trong [hợp đồng nhóm](../docs/SHARED.md); ID hợp lệ chuẩn hóa về ObjectId hex thường, [kiểm chứng](../docs/dat/ID_NORMALIZATION.md).
- [ ] Script seed Redis: **≥ 50 Hash** tiến trình đọc + **1 ZSET 50 cuốn sách** kèm lượt đọc (phối hợp Sơn, dùng `bookId` thật từ Mongo) — fixture riêng đã đạt 50/50, chưa có manifest/tích hợp dữ liệu Sơn; [audit và giới hạn](../docs/dat/ACCEPTANCE_RESULTS.md).
- [x] Thử các lệnh cơ bản trên Redis Insight, ghi lại lệnh mẫu — [ảnh Hash/ZSET/session và lệnh S03](../docs/dat/ACCEPTANCE_RESULTS.md).

## Phase 2 (trọng tâm – barem mục 3, 2.5đ)
### A. Lưu tiến trình đọc dở (Redis Hashes)
- [x] `PUT /api/progress/{userId}/{bookId}` → `HSET progress:{userId}:{bookId} chapter page line updatedAt` — auth/validation và ID hoa/thường cùng Hash đã qua; [P01–P06/F02](../docs/dat/ID_NORMALIZATION.md).
- [x] `GET /api/progress/{userId}/{bookId}` → `HGETALL`, trả về tiến trình đã lưu — PUT alias trang30 rồi GET chuẩn đúng trang30; [regression](../docs/dat/ID_NORMALIZATION.md). Dữ liệu alias cũ chưa migration.
- [ ] (Tùy chọn) `GET /api/progress/{userId}` → danh sách sách đang đọc dở — chưa chọn/triển khai, không phải thiếu bắt buộc; [phạm vi](../docs/dat/PLAN.md).

### B. Bảng xếp hạng sách đọc nhiều nhất (Redis ZSET)
- [x] `POST /api/books/{bookId}/read` → `ZINCRBY ranking:books 1 {bookId}` khi mở chương — API hoa/thường cùng member score2, 40 request đồng thời không mất điểm; [R01/R02](../docs/dat/ID_NORMALIZATION.md). Sự kiện UI mở chương vẫn chờ Sơn.
- [ ] `GET /api/ranking?top=10` → `ZREVRANGE ranking:books 0 N-1 WITHSCORES`, trả `bookId` và `score`; Sơn ghép thông tin sách — API/top/batch metadata đạt, phần Sơn ghép trên web chưa xong; [R03/R05](../docs/dat/ACCEPTANCE_RESULTS.md).
- [ ] (Tùy chọn) Chống tăng điểm lặp quá nhanh: khóa `SET NX EX` theo user + chương — chưa chọn/triển khai; D03 tính từng request, [quyết định](../docs/dat/DECISIONS.md).

### C. Kiểm thử hiệu năng (phối hợp Sơn)
- [x] Đo độ trễ lấy tiến trình: Redis vs Mongo (ví dụ 1000 lần) — chỉ fixture riêng: warm-up200, 1000 mẫu/backend, raw/summary tái lập; chưa đo dữ liệu Sơn. [B01 và số liệu](../docs/dat/ACCEPTANCE_RESULTS.md).
- [ ] Ghi kết quả cho Vũ đưa vào báo cáo — đã lưu raw/summary, chưa có xác nhận bàn giao Vũ; [I03](../docs/dat/ACCEPTANCE_RESULTS.md).

### D. Demo
- [ ] Đọc liên tục một cuốn sách để ZSET tăng điểm, BXH nhảy vị trí — API/Redis đã chứng minh tăng điểm, chưa demo UI/nhóm hoặc tổng duyệt; [I01–I03](../docs/dat/ACCEPTANCE_RESULTS.md).

## Definition of Done
- Đóng/mở lại sách → trả về đúng trang đã lưu.
- Redis Insight thấy điểm ZSET tăng theo từng lần đọc.

Cập nhật 22/10/2026: các dòng Definition of Done là tiêu chí gốc, chưa hoàn thành toàn bộ. Backend và fixture riêng có bằng chứng; còn migration alias cũ, manifest Sơn, UI và tổng duyệt. [Checkpoint](../docs/dat/PROGRESS.md), [kết quả hiện tại](../docs/dat/ACCEPTANCE_RESULTS.md).
