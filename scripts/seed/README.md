# Seed dữ liệu MongoDB (Sơn – Phase 1, barem mục 4)

Nạp **60 đầu sách** (mặc định), mỗi sách **5–10 chương** toàn văn (~5–9 nghìn ký tự/chương) và **2–4 mục/chương** vào collection `books`.

## Chạy

```bash
docker compose up -d                       # từ thư mục gốc, chờ mongodb healthy
cd scripts/seed
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed_books.py
```

Kết nối lấy từ biến môi trường `MONGO_URI`, mặc định khớp Docker Compose
(`mongodb://admin:admin123@localhost:27017/digital_library?authSource=admin`).
Nếu máy có MongoDB khác chiếm cổng 27017, xem cách đổi cổng trong `docs/SHARED.md` mục 5 rồi truyền `--uri`.

| Lệnh | Tác dụng |
|---|---|
| `python seed_books.py` | Nạp 60 sách. Chạy lại bao nhiêu lần cũng không bị nhân đôi |
| `python seed_books.py --count 80` | Nạp 80 sách (barem: 50–100) |
| `python seed_books.py --reset` | Xóa các sách seed cũ rồi nạp lại (không đụng sách admin tạo qua API) |
| `python seed_books.py --dry-run` | Chỉ sinh dữ liệu và kiểm tra schema, không ghi DB |
| `python seed_books.py --seed 7` | Đổi hạt giống: cùng seed cho ra cùng dữ liệu |

## Thiết kế

- **ID cố định.** Sách thứ *n* có `_id = b00c` + *n* (hex 20 chữ số), ví dụ `b00c00000000000000000001`.
  Nhờ vậy chạy lại không đổi ID và Redis không bị mồ côi `bookId`.
- **Idempotent.** Ghi bằng `ReplaceOne(upsert=True)` theo `_id`.
- **Đúng schema.** `chapterNo`, `sectionNo` là int32 (không phải double như mongosh mặc định), `createdAt`/`updatedAt` là `date`.
  Script tự kiểm tra theo `backend/.../mongo/books.schema.json` trước khi ghi, và áp cùng validator như backend.
- **Index** (text, categories, createdAt) do backend tạo khi khởi động. Hãy chạy backend ít nhất một lần để tìm kiếm `?q=` hoạt động.
- **Nội dung** sinh theo 10 thể loại (Văn học, Khoa học viễn tưởng, Trinh thám, Lịch sử, Thiếu nhi, Du ký, Khoa học, Công nghệ, Kinh tế, Tâm lý - Kỹ năng); không cần mạng. Đây là văn bản mẫu, không phải tác phẩm thật.
- `coverUrl` trỏ tới `picsum.photos` (ảnh giữ chỗ, cần internet); frontend nên có ảnh dự phòng nếu tải lỗi.

## Bàn giao cho Đạt (Redis)

`book_ids.json` liệt kê `bookId` của các sách seed (cùng `--seed` và `--count` mặc định thì ID luôn giống nhau). Script sẽ ghi đè file này mỗi lần chạy thật.
Đạt đọc file này để seed **≥ 50 Hash** `progress:{userId}:{bookId}` và **ZSET `ranking:books` gồm 50 sách**.

## Kiểm tra bằng MongoDB Compass

Kết nối `mongodb://admin:admin123@localhost:27017/?authSource=admin` → `digital_library` → `books`:
- Số document = 60 (hoặc số đã chọn).
- Mở một sách: `chapters` là mảng 5–10 phần tử, mỗi phần tử có `chapterNo` (Int32), `title`, `content`, `sections`.
- Tab *Validation* hiển thị JSON Schema; thử sửa `chapterNo` thành số thực sẽ bị từ chối.
