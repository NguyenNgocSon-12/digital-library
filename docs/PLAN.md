# Kế hoạch triển khai 2 phase

> Phase 2 là bản **phát triển tiếp từ Phase 1** (tổng hợp = Phase 1 + phần mới).

## Phase 1 – Nền tảng (trình bày tuần 1)
**Mục tiêu:** Có thiết kế CSDL hoàn chỉnh, hạ tầng chạy được, CRUD trên MongoDB và dữ liệu mẫu.

| # | Công việc | Phụ trách | Barem |
|---|---|---|---|
| 1 | Docker Compose + khung repo | Cả nhóm | – |
| 2 | Giải trình kiến trúc Polyglot Persistence | Vũ | 1.0đ |
| 3 | Thiết kế JSON Schema Mongo (books, chapters/sections, users) + thiết kế Redis (Hash, ZSET) | Vũ | 1.5đ |
| 4 | CRUD sách, thêm chương, CRUD độc giả (API) | Vũ | 2.5đ |
| 5 | Script seed 50–100 sách × 5–10 chương | Sơn | 1.0đ (một phần) |
| 6 | Giao diện quản lý sách + danh sách/đọc cơ bản | Sơn | – |
| 7 | Chuẩn bị Redis: kết nối, module khung, seed 50 Hash + 1 ZSET 50 sách | Đạt | 1.0đ (một phần) |
| 8 | Quan sát dữ liệu bằng Compass & Redis Insight | Sơn | – |

**Deliverable Phase 1:** báo cáo thiết kế, API CRUD chạy được, dummy data nạp xong, demo CRUD.

## Phase 2 – Tính năng nâng cao & hoàn thiện (trình bày tuần 2)
**Mục tiêu:** Tích hợp Redis, giao diện E-Reader, kiểm thử hiệu năng, demo sống.

| # | Công việc | Phụ trách | Barem |
|---|---|---|---|
| 1 | API lưu/đọc tiến trình đọc (Redis Hashes) | Đạt | 1.25đ |
| 2 | API tăng lượt đọc `ZINCRBY` + Top sách `ZREVRANGE` | Đạt | 1.25đ |
| 3 | Tích hợp: mở chương → gọi tăng điểm ZSET; đóng/chuyển trang → lưu Hash | Đạt + Sơn | – |
| 4 | Giao diện E-Reader (tự cuộn đến trang đã lưu, BXH Top sách) | Sơn | – |
| 5 | Đo hiệu năng: so sánh độ trễ Redis vs Mongo khi lấy tiến trình | Sơn + Đạt | 1.0đ (một phần) |
| 6 | Hoàn thiện báo cáo (bổ sung kết quả đo) | Vũ | – |
| 7 | Tổng duyệt kịch bản demo ≥ 2 lần | Sơn (điều phối) | 1.5đ |

**Deliverable Phase 2:** hệ thống hoàn chỉnh, dummy data đạt chuẩn, demo sống trơn tru, báo cáo cuối.

## Checklist barem (tự đánh giá)
- [ ] Giải trình Polyglot (1.0)
- [ ] Schema Mongo + cấu trúc Redis (1.5)
- [ ] CRUD sách / chương / độc giả (2.5)
- [ ] Redis Hashes – tiến trình đọc (1.25)
- [ ] Redis ZSET – BXH (1.25)
- [ ] Dummy data: ≥50 sách × 5–10 chương; ≥50 Hash; 1 ZSET 50 sách (1.0)
- [ ] Demo sống (1.5)
