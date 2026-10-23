# Kế hoạch phần Đạt

Ngày đối chiếu: 22/10/2026 (Asia/Saigon). Trạng thái cập nhật: API và fixture/benchmark độc lập đã triển khai, xem RESULTS.md; tích hợp Sơn/UI còn chờ. Các bảng hiện trạng clone bên dưới được giữ làm lịch sử.

## Nguồn và hiện trạng

| Nguồn | Nội dung dùng để lập kế hoạch |
|---|---|
| `members/DAT.md` | Phase 1 Redis/seed/lệnh mẫu; Phase 2 progress, ranking, đo hiệu năng, demo |
| `docs/PLAN.md` | Hash 1.25đ, ZSET 1.25đ; seed và đo phối hợp Sơn; tiến độ hai phase |
| `docs/SHARED.md` mục 1–4, 6 | Sở hữu, DTO, auth, kiểm tra sách, hợp đồng tích hợp |
| `docs/ARCHITECTURE.md` mục 3–4 | Key, kiểu Redis, TTL, AOF; số liệu hiệu năng còn chờ |
| `members/SON.md`, `members/VU.md`, `docs/DEMO_SCRIPT.md` | Phụ thuộc seed/giao diện, báo cáo và demo trang 30 |
| Mã nguồn `reading/`, `ranking/`, `catalog/service/BookService.java`, `identity/auth/`, `common/` | Module Đạt chỉ có package-info; nền catalog, auth và lỗi đã tồn tại |

Không tìm thấy AGENTS hay thư mục nguồn riêng trong repo lúc clone; AGENTS ở gốc được tạo trong bước hồ sơ này. `backend/README.md` nói chỉ có health đã lỗi thời so với code; không dùng câu đó để đánh giá catalog/identity chưa làm.

## Git đã kiểm tra

| Nhánh remote | Commit tại thời điểm clone | So với main |
|---|---|---|
| `origin/main` (HEAD mặc định) | `4a0dd9b31fdc17601e2891f5acf28f69b4d98954` | Nền mới nhất, merge PR #2 |
| `origin/develop` | `5b1bec0c80d4a4cf505e348a1399efe600c81e57` | Chậm 5 commit, không có commit riêng |
| `origin/dev/thai-duy-vu` | `6ef26a9c03187e706830176f4c0e5f98f28d870b` | Chậm 1 merge commit, không có commit riêng |

Đã đối chiếu `git ls-remote --heads origin`. Nhánh local `codex/dat-work-dossier` lấy từ main; chưa push/PR. Quy ước repo vẫn PR vào develop. Trước triển khai/PR cần fetch lại và thống nhất cập nhật develop hoặc cách lấy nền; không tự gộp nhánh chung. Nếu vẫn PR nền main vào develop cũ, diff sẽ kéo theo cả phần Vũ.

## Các mốc tiếp theo

| Mốc | Công việc | Điều kiện hoàn thành |
|---|---|---|
| 0 — Hồ sơ | Tạo AGENTS và 5 tài liệu docs/dat; truy vết nguồn, quyết định, checkpoint | Đủ file, link nội bộ hợp lệ, chỉ diff tài liệu |
| 1 — Nền chạy | Kiểm tra Git mới; JDK/wrapper, Docker daemon/cổng, Mongo/Redis; baseline test | Ghi lệnh/kết quả hoặc blocker cụ thể; không tự đổi nền framework |
| 2 — Hợp đồng | Chốt D01–D05 trong DECISIONS trước phần phụ thuộc | Request/response, status, quyền, biên top và sự kiện mở chương được ghi rõ |
| 3 — Progress | DTO/controller/service/Redis trong reading; auth và validation; test tương ứng | P01–P06 trong ACCEPTANCE; ghi bằng chứng Redis thật |
| 4 — Ranking | Controller/service/Redis trong ranking; tăng nguyên tử; Top N; test | R01–R05 theo hợp đồng đã chốt |
| 5 — Seed | Phối hợp Sơn có dữ liệu Mongo trước; chuẩn bị seed Redis có kiểm soát và lệnh Insight | S01–S03; ≥50 Hash, 1 ZSET 50 bookId hợp lệ |
| 6 — Đo | Cùng Sơn thiết kế phép đo tương đương Redis/Mongo, chạy và lưu raw data | B01; không tự tạo ngưỡng ms hoặc kết luận Redis nhanh hơn |
| 7 — Tích hợp/bàn giao | Sơn nối E-Reader/BXH; demo hai lần; cập nhật SHARED và hướng dẫn thực tế | I01–I03; phân biệt API đạt với UI còn chờ |

Mỗi mốc cập nhật PROGRESS; chỉ triển khai sau yêu cầu tiếp theo của người dùng. Không ấn định thời hạn lịch khi chưa có lịch nhóm.

## File dự kiến khi triển khai (chưa tạo)

- `reading/`: DTO lưu/trả tiến trình, controller, service và lớp truy cập Redis nếu cần.
- `ranking/`: DTO bookId/score, controller, service và lớp truy cập Redis nếu cần.
- Test tương ứng trong `backend/src/test/java/.../reading/`, `ranking/`; integration test với Redis/Mongo thật khi môi trường sẵn sàng.
- Seed thuộc `scripts/seed/` phối hợp Sơn; phép đo và raw data đặt vị trí thống nhất với Sơn, không thêm dữ liệu benchmark vào domain nghiệp vụ.
- `docs/SHARED.md` cập nhật ví dụ response thật cùng thay đổi API; `docs/dat/` cập nhật kết quả. Cấu hình dùng chung chỉ sửa khi có nhu cầu đã xác định.

Không triển khai hai mục tùy chọn (danh sách sách đang đọc, chống lặp SET NX EX) như điều kiện nghiệm thu bắt buộc. Không sửa frontend thay Sơn hoặc làm lại auth của Vũ.
