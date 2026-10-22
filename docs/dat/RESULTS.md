# Kết quả phần Đạt — 22/10/2026

**Bản nghiệm thu hiện tại:** [ACCEPTANCE_RESULTS.md](ACCEPTANCE_RESULTS.md) — 14 Đạt/0 Chưa đạt/4 Bị chặn sau [sửa F01/F02](ID_NORMALIZATION.md) và regression thật. Dữ liệu alias cũ chưa migration; manifest Sơn/UI/tổng duyệt còn chờ. Nội dung bên dưới giữ kết quả lượt20:22 làm lịch sử.

Nền `4a0dd9b`, working tree chưa commit trên `codex/dat-work-dossier`. D01–D05 được người dùng xác nhận trong chat; xem DECISIONS. JDK 21.0.8, Maven 3.10.0, Spring Boot 4.1.1; Mongo 7.0.43 và Redis 7.4.11 trong container riêng của repo.

| Nhóm | Kết quả / bằng chứng | Giới hạn |
|---|---|---|
| P01–P06 | Đạt backend: full context, auth/token thật, Mongo/Redis thật, không mock domain. Hash đúng field/UTC/TTL, ghi đè/cách ly, lỗi 400/401/403/404, admin/user/chương | Không kiểm chứng phân trang hay khôi phục trình duyệt |
| R01–R04 | Đạt backend: tăng nguyên tử 40/40 request đồng thời, 1→41; rỗng/top=1/10/100/hòa điểm và biên/sai kiểu | Chính sách tính theo từng request, chưa dedupe |
| R05 | Đạt phần API: sách sai/mất không ghi ZSET | UI batch bỏ qua sách đã xóa chưa tích hợp |
| S01–S02 | Đạt fixture riêng: 50 sách×5 chương, 50 Hash, 50 member; rerun reset dữ liệu fixture đã đổi, sentinel ngoài registry giữ nguyên | Chưa dùng manifest Sơn |
| S03 | CLI SCAN/HGETALL/TTL/ZCARD/ZREVRANGE đã chạy; lệnh ở scripts/dat/README | Chưa thực hiện quan sát/ảnh Redis Insight |
| B01 | Đạt phép đo fixture riêng: warm-up=200/backend, N=1000/backend, concurrency=1, 2000 mẫu, 0 lỗi | Chưa đo dữ liệu Sơn hoặc tải production |
| I01–I03 | Bị chặn: chờ Sơn tích hợp UI, dữ liệu nhóm và tổng duyệt hai lần | Không lấy backend test thay demo |

Kiểm thử: baseline catalog 5/5; full suite sau sửa strict integer 29/29, không skip, gồm 13 ca ProgressApiTest, 9 RankingApiTest, 5 catalog, contextLoads và integration thật. Tool fixture bổ sung được biên dịch và chạy riêng thành công cho seed, nhận manifest/rerun và benchmark. Không đổi dependency/framework.

Integration cuối dùng Mongo `digital_library_dat_test`, Redis DB15. A=`6ada0c83fbebec9e0e825068`, B=`6ada0c83fbebec9e0e825069`; sách A=`6ada0c84fbebec9e0e82506b`, B=`6ada0c84fbebec9e0e82506c`. Sau test có lần cố ý hòa điểm A/B=41. Smoke TCP HTTP sau đó tăng A thêm 1; Hash integration A chương1/trang31/line2 không đổi. Smoke tạo user riêng và lưu chương3/trang30/line0; xem [HTTP thực](evidence/http-smoke.json), không chứa token/mật khẩu.

## Phép đo local lúc 20:22 +07

| Backend | Mean ms | Median ms | p95 ms |
|---|---:|---:|---:|
| Mongo | 0.8973194 | 0.7742 | 1.6920 |
| Redis | 0.5587119 | 0.5009 | 0.9488 |

Chỉ mô tả lần đo này. Windows 11, i5-12500H, 16 logical processors, RAM 16869543936 byte; Docker Desktop cùng máy, Redis AOF, Mongo có index `_id`. Các ứng dụng/container khác vẫn chạy; không đo cold cache hay cô lập tải. Hai client kết nối lâu dài, cùng payload bốn string field, tuần tự và đảo thứ tự đọc. Không gồm HTTP/auth/catalog. Không có SLA trong nguồn.

- [Manifest ID thật](evidence/fixture/manifest.json)
- [Kiểm chứng seed/reset/sentinel](evidence/fixture/seed-verification.json)
- [Raw samples](evidence/fixture/benchmark-raw.csv) và [summary](evidence/fixture/benchmark-summary.json)
- [Lệnh chạy và nhận manifest Sơn](../../scripts/dat/README.md)

Không commit/push/PR trong lượt triển khai. `develop` thiếu 5 commit của main sau fetch; cần kiểm tra lại nền trước PR để tránh kéo phần Vũ vào diff. Mongo/Redis repo còn chạy; Java server kiểm thử đã được dừng. Không reset usage, không xóa volume, không sửa frontend hoặc scripts/seed của Sơn.
