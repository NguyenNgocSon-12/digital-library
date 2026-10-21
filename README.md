# 📚 Hệ thống Thư viện số & Đọc sách trực tuyến (Polyglot Persistence)

> Đồ án môn **NoSQL** – Đề tài 15 | Nhóm 3 thành viên: **Vũ – Đạt – Sơn**
> CSDL: **MongoDB** (nội dung sách) + **Redis** (tiến trình đọc, bảng xếp hạng)

## 1. Giới thiệu
Cổng đọc sách điện tử trực tuyến cho phép:
- Quản lý kho sách phong phú (sách → chương → mục) trên MongoDB.
- Lưu **tiến trình đọc dở** của từng độc giả, mở lại tức thì (Redis Hashes).
- Hiển thị **bảng xếp hạng sách thịnh hành** theo lượt đọc (Redis Sorted Set).

## 2. Kiến trúc Polyglot Persistence
| Loại dữ liệu | CSDL | Lý do |
|---|---|---|
| Sách, chương, mục, tài khoản độc giả (dữ liệu lâu dài, cấu trúc lồng nhau, văn bản lớn) | **MongoDB** | Document model lưu lồng nhau tự nhiên, schema linh hoạt, truy vấn/index trên văn bản |
| Tiến trình đọc dở (dữ liệu trạng thái, ghi/đọc liên tục) | **Redis Hashes** | In-memory, độ trễ < 1ms, ghi đè từng field |
| Bảng xếp hạng lượt đọc (dữ liệu tạm, cần sắp xếp realtime) | **Redis ZSET** | `ZINCRBY` + `ZREVRANGE` tự duy trì thứ tự, O(log N) |

Chi tiết: xem [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 3. Công nghệ (đề xuất – nhóm có thể đổi)
- Backend: Node.js (Express) + `mongodb`/`mongoose` + `ioredis`
- Frontend: HTML/JS thuần hoặc React (giao diện E-Reader)
- Hạ tầng: Docker Compose; công cụ quan sát: MongoDB Compass, Redis Insight

## 4. Khởi chạy nhanh (cho cả 3 thành viên)
```bash
git clone git@github.com:ThaiDuyVu/digital-library.git && cd digital-library
cp .env.example .env
docker compose up -d
docker compose ps        # kiểm tra mongodb, redis healthy
```
| Dịch vụ | Địa chỉ |
|---|---|
| MongoDB | `mongodb://admin:admin123@localhost:27017/?authSource=admin` (dùng Compass) |
| Redis | `localhost:6379` |
| Redis Insight | http://localhost:5540 (add DB: host `redis`, port `6379`) |
| Mongo Express | http://localhost:8081 |

Dừng: `docker compose down` (giữ dữ liệu) | Xóa sạch: `docker compose down -v`

## 5. Cấu trúc thư mục
```
digital-library/
├── README.md
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── ARCHITECTURE.md     # Giải trình Polyglot + thiết kế schema (barem mục 1)
│   ├── PLAN.md             # Kế hoạch 2 phase + barem checklist
│   └── DEMO_SCRIPT.md      # Kịch bản demo bảo vệ
├── members/
│   ├── VU.md               # SV1 – Data Architect & CRUD Lead
│   ├── DAT.md              # SV2 – Advanced Query Specialist (Redis)
│   └── SON.md              # SV3 – Fullstack Integrator & DB Tester
├── backend/                # API (Vũ: mongo/, Đạt: redis/)
├── frontend/               # Giao diện E-Reader (Sơn)
└── scripts/seed/           # Script nạp dummy data (Sơn)
```

## 6. Phân công
| Thành viên | Vai trò | File nhiệm vụ |
|---|---|---|
| Vũ | SV1 – Data Architect & CRUD Lead | [members/VU.md](members/VU.md) |
| Đạt | SV2 – Advanced Query Specialist | [members/DAT.md](members/DAT.md) |
| Sơn | SV3 – Fullstack Integrator & DB Tester | [members/SON.md](members/SON.md) |

## 7. Quy ước làm việc với GitHub
- Nhánh: `main` (ổn định) ← `develop` ← `feature/<ten>-<chuc-nang>` (vd `feature/vu-book-crud`).
- Mỗi người làm trên nhánh riêng, tạo **Pull Request** vào `develop`, ít nhất 1 người review.
- Cuối mỗi phase: merge `develop` → `main`, gắn tag `phase-1`, `phase-2`.
- Commit message: `feat:`, `fix:`, `docs:`, `chore:` + mô tả ngắn.
- Không commit file `.env`.
- Quy ước thư mục để tránh xung đột: Vũ sửa `backend/src/mongo/`, Đạt sửa `backend/src/redis/`, Sơn sửa `frontend/` và `scripts/`.

## 8. Lộ trình
2 phase, mỗi phase trình bày 1 tuần. Xem [`docs/PLAN.md`](docs/PLAN.md).
