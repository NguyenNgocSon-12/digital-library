# Kịch bản demo sống

**Chuẩn bị trước:** `docker compose up -d`, nạp dummy data, mở sẵn Compass, Redis Insight, web E-Reader.

## Kịch bản 1 – Lưu tiến trình đọc (Redis Hashes)
1. **Vũ** đăng nhập, đọc 1 cuốn sách đến **Trang 30**, rồi **đóng trình duyệt**.
2. **Sơn** mở lại sách → hệ thống **tự cuộn đến Trang 30** (truy xuất tức thì từ Redis Hash).
3. (Tùy chọn) Sơn mở Redis Insight cho thấy key `progress:{userId}:{bookId}`.

## Kịch bản 2 – Bảng xếp hạng (Redis ZSET)
1. **Sơn** mở Redis Insight, mở key `ranking:books`, ghi nhận điểm hiện tại.
2. **Đạt** đọc liên tục một cuốn sách (mở nhiều chương).
3. Sơn refresh Insight → điểm tăng, BXH **nhảy vị trí**; web hiển thị Top sách cập nhật.

## Phân vai
| Vai | Người |
|---|---|
| Điều phối + thao tác công cụ | Sơn |
| Đọc đến trang 30 | Vũ |
| Đọc liên tục cho ZSET | Đạt |

## Dự phòng
- Chuẩn bị sẵn tài khoản + sách cố định cho demo.
- Quay video demo dự phòng.
- Kiểm tra lại bằng `docker compose ps` trước giờ bảo vệ.
