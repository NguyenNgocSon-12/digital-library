# Kiến trúc & thiết kế CSDL (Vũ hoàn thiện)

## 1. Giải trình Polyglot Persistence (1.0đ)
_TODO – Vũ: nêu rõ vì sao MongoDB lưu nội dung toàn văn, Redis lưu trạng thái tạm/BXH; so sánh với dùng 1 CSDL duy nhất; luồng dữ liệu giữa 2 hệ thống; đánh đổi (consistency, mất dữ liệu Redis…)._

Sơ đồ luồng (vẽ lại bằng draw.io / mermaid):
```
Client ──► API ──┬─► MongoDB  (sách, chương, độc giả)
                 └─► Redis    (progress:*, ranking:books)
```

## 2. Thiết kế MongoDB (1.5đ – phần 1)
Collections đề xuất (Vũ chốt lại):
- `books`: `_id, title, author, category[], description, coverUrl, createdAt, chapters[ {chapterNo, title, content, sections[ {sectionNo, heading, text} ]} ]`
- `users`: `_id, username, email, passwordHash, fullName, createdAt`

_TODO – Vũ: viết JSON Schema validator đầy đủ, nêu lý do embed chương trong sách (5–10 chương) và giới hạn 16MB/document, danh sách index._

## 3. Thiết kế Redis (1.5đ – phần 2)
| Key | Kiểu | Ví dụ | Mục đích |
|---|---|---|---|
| `progress:{userId}:{bookId}` | Hash | `chapter=3, page=30, updatedAt=...` | Tiến trình đọc dở |
| `ranking:books` | ZSET | member=`bookId`, score=lượt đọc | BXH sách thịnh hành |

Lệnh chính: `HSET/HGETALL`, `ZINCRBY`, `ZREVRANGE ... WITHSCORES`.

_TODO – Vũ + Đạt: chốt quy ước đặt tên key, TTL (nếu có), chiến lược đồng bộ về Mongo (nếu làm)._
