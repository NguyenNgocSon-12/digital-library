# Bàn giao phần Đạt — 22/10/2026

## Trạng thái hiện tại

Backend reading/ranking đã triển khai và sửa F01/F02. [Nghiệm thu từng ID](ACCEPTANCE_RESULTS.md): **14 Đạt, 0 Chưa đạt, 4 Bị chặn** trong phạm vi đã kiểm chứng. Đây không phải hoàn thành toàn hệ thống.

| Phần | Trạng thái |
|---|---|
| Backend P01–P06, R01–R04 | Đạt với Mongo/Redis thật; ID hoa/thường cùng tài nguyên, quyền và lỗi vẫn đúng |
| R05 | API/batch đã đạt; toàn mục Bị chặn vì UI chưa ghép/bỏ sách mất |
| S01–S03, B01 | Đạt fixture riêng và Redis Insight; chưa xác nhận dữ liệu/manifest Sơn |
| I01–I03 | Bị chặn: UI đọc/khôi phục/BXH, hai lần tổng duyệt và xác nhận bàn giao số liệu Vũ |
| Alias legacy | Chưa migration; giữ nguyên Hash/member/score cũ, cần duyệt quy tắc và phạm vi trước apply |
| Tùy chọn | Danh sách progress theo user và chống lặp chưa triển khai; không phải điều kiện bắt buộc |

[members/DAT.md](../../members/DAT.md) đã đồng bộ: 7 mục [x], 6 mục [ ] có lý do/link. Dòng seed phối hợp Sơn và BXH có phần ghép UI vẫn [ ] dù fixture/API riêng đạt. AGENTS yêu cầu đồng bộ checklist sau từng mốc, không đổi phân công gốc.

## Git và phạm vi bàn giao

- Nhánh local `codex/dat-work-dossier`, HEAD `4a0dd9b31fdc17601e2891f5acf28f69b4d98954`. Người dùng đã giao stage/review/commit local trong lượt tiếp theo; nội dung triển khai nằm trong commit `feat: implement Redis reading progress and book ranking` trên nhánh này (tra SHA bằng git log). Chưa push hoặc tạo PR.
- Rà cuối đã fetch origin: `origin/main...origin/develop` = `5 0`, develop thiếu 5 commit nền main. Không tự merge/rebase/push nhánh chung. Trước PR vào develop phải phối hợp cập nhật nền hoặc dựng nhánh chỉ có thay đổi Đạt trên nền đã thống nhất, rồi kiểm tra lại diff. Cần ít nhất một reviewer.
- Production chỉ thêm reading/ranking; test tương ứng; script độc lập ở scripts/dat. File chung docs/SHARED công bố contract và invariant ID; members/DAT/AGENTS/docs/dat là hồ sơ/tiến độ. Không sửa catalog/identity/common, dependency, frontend hoặc scripts/seed của Sơn.
- [Nội dung commit/PR soạn sẵn](COMMIT_PR_DRAFT.md). Người dùng đã giao tạo commit local theo bản nháp; chưa push hoặc tạo PR. Các file mới đã được rà cùng staged diff; loại bản inventory chẩn đoán sai, log và build output khỏi commit.

## Cách chạy local

Từ gốc repo, chỉ chạy khi cần tiếp tục tích hợp; các lệnh dưới không được thực thi lại trong lượt rà cuối:

```powershell
# Chỉ tạo .env nếu chưa có; kiểm tra đích DB/cổng trước khi chạy.
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose up -d mongodb redis redisinsight
docker compose ps
$env:JAVA_HOME = 'C:/Program Files/Android/openjdk/jdk-21.0.8'
& "$env:JAVA_HOME/bin/java.exe" -version
Set-Location backend
.\mvnw.cmd -v
.\mvnw.cmd spring-boot:run
```

JDK trên là đường đã kiểm chứng tại máy này, không phải yêu cầu đường dẫn trên máy nhóm; cần JDK17+. Wrapper Maven3.10.0, Spring Boot4.1.1 giữ nguyên. Backend mặc định8080, Mongo27017, Redis6379, Insight5540. Spring không tự nạp .env: nếu Compose thay cổng/credentials/database, đặt MONGO_URI/REDIS_URL/SERVER_PORT tương ứng trong process backend. Không dùng nhầm Mongo27018/Redis6380 của Học Liệu Số. Không lưu token/mật khẩu thật vào hồ sơ.

Frontend do Sơn tiếp tục: từ gốc `cd frontend`, `npm ci`, `npm run dev`; Vite mặc định5173 và proxy API8080. ReadingPage/RankingPage hiện là placeholder; khởi động frontend không chứng minh đã tích hợp. Backend mặc định tạo admin theo cấu hình identity khi chưa có; tài khoản fixture seed riêng không dùng đăng nhập.

Runtime được giữ từ các lượt trước: Mongo/Redis repo, Redis Insight và các Redis container test riêng; Java server smoke đã dừng. Không khởi động/dừng dịch vụ hoặc sửa dữ liệu trong lượt rà cuối. Không dùng FLUSH hoặc xóa volume.

## Hợp đồng API để Sơn tích hợp

| API | Quyền và request | Kết quả |
|---|---|---|
| PUT `/api/progress/{userId}/{bookId}` | Bearer token, chính chủ/admin; `{chapter:3,page:30,line:0}` dạng JSON với tên trường có dấu nháy, số nguyên; chapter/page>=1,line>=0 | 200 `{chapter,page,line,updatedAt}`; chương/sách phải tồn tại; admin target user phải tồn tại |
| GET `/api/progress/{userId}/{bookId}` | Bearer token, chính chủ/admin | 200 cùng DTO; chưa lưu404 NOT_FOUND |
| POST `/api/books/{bookId}/read` | Công khai, không cần body; một request cho một lần mở chương | 200 `{bookId,score}`; ZINCRBY+1, reload/retry cũng tăng, chưa dedupe |
| GET `/api/ranking?top=10` | Công khai, top1–100 | 200 mảng `{bookId,score}` giảm theo score; hòa điểm theo member giảm dần Redis |

Ví dụ PUT hợp lệ: `{"chapter":3,"page":30,"line":0}`. updatedAt do server sinh ISO8601 UTC; Hash bốn field, không TTL trong demo. Key production `progress:{userId}:{bookId}` và `ranking:books`. ID hợp lệ chuẩn hóa ObjectId hex thường trước đọc/ghi/key, trước canAccess và trong bookId trả về; không đổi lỗi ID sai.

Lỗi `{code,message}`: thiếu/sai token401, khác chủ không phải admin403 trước lookup, ID sai/mất sách/user theo quyền404, request sai/thiếu/null/chuỗi số/số thực hoặc top ngoài biên400. Chưa đặt max page/line theo phân trang frontend. Chưa có cleanup khi xóa sách/user. Health chỉ chứng minh ứng dụng trả lời, không thay kiểm tra chức năng.

Ranking không chứa metadata sách. Sơn lấy ID từ ranking rồi gọi `GET /api/books/batch?ids=id1,id2` (tối đa100), ghép bằng id và giữ thứ tự ranking; batch bỏ qua ID mất nên kết quả hiển thị có thể ít hơn N. Endpoint read chưa nhận chapter: phía UI quyết định khi nào phát sự kiện mở chương, tránh gọi do re-render. Không tự đổi D01–D08; chi tiết [SHARED](../SHARED.md) và [DECISIONS](DECISIONS.md).

## Bằng chứng kiểm thử hiện có

Không chạy lại test đã đạt khi code/môi trường liên quan chưa đổi. Lượt rà cuối chỉ đối chiếu artifact/fingerprint, link và Git, không dùng build làm bằng chứng chức năng.

| Bằng chứng | Kết quả/giới hạn |
|---|---|
| [F01/F02](evidence/acceptance/20261022205242_361ca5b9/api-redis-evidence.json) | 1 regression qua: POST ID hoa/thường cùng member score2, batch ghép metadata; PUT alias page30, GET chuẩn/hoa30 |
| [userId/auth](evidence/acceptance/20261022205402_142d850b/api-redis-evidence.json) | 1 regression qua: chính chủ/admin qua ID hoa, người khác403; invalid ID giữ lỗi; legacy ranking DTO chuẩn nhưng data không đổi |
| [P/R liên quan](evidence/acceptance/20261022205450_1860e247/api-redis-evidence.json) | 23 ca qua,0 lỗi;2 review skip trong run chung vì đã chạy riêng. Có40 request đồng thời, top12→10, validation/auth, deleted book/batch |
| [HTTP TCP smoke](evidence/http-smoke.json) | PUT/GET trang30,401 và POST read thực; bằng chứng trước sửa ID, không thay regression mới |
| [Fixture audit](evidence/acceptance/benchmark/fixture-audit.json), [seed reset](evidence/fixture/seed-verification.json) | 50 Hash/50 sách thật trong fixture, TTL-1; reset riêng fixture/sentinel được bảo toàn; chưa dùng manifest Sơn |
| [Insight Hash](evidence/acceptance/redis-insight-hash.png), [ZSET](evidence/acceptance/redis-insight-ranking.png), [session TYPE](evidence/acceptance/redis-insight-session-type.png) | S03 thật; không chứa token hoặc giá trị session |
| [Raw CSV](evidence/acceptance/benchmark/benchmark-raw.csv), [summary](evidence/acceptance/benchmark/benchmark-summary.json), [tính lại](evidence/acceptance/benchmark/raw-summary-check.json) | Warm-up200/backend,1000 mẫu/backend,concurrency1,0 lỗi; summary khớp phép tính độc lập |

Các run regression/P/R có environment.json và production-checksums.json cạnh evidence. MockMvc dùng full Spring context/login/Mongo/Redis thật, không phải browser/TCP demo. Test đỏ [review20:46](INDEPENDENT_REVIEW.md) được giữ làm lịch sử, không dùng làm trạng thái hiện tại.

Phép đo local20:36: Mongo mean1.0326982/median0.9004/p95 1.8855ms; Redis mean0.6219189/median0.5332/p95 1.1874ms. Windows11,JDK21.0.8,Mongo7.0.43,Redis7.4.11/AOF; cùng50 vị trí/bốn string field, kết nối lâu dài, đảo thứ tự đọc. Không gồm HTTP/auth/catalog, không cô lập tải/cold cache và không có SLA. Code benchmark độc lập không đổi sau sửa ID; không chạy đo lại chỉ để làm mới ngày.

## Tái lập khi có thay đổi cần kiểm tra

```powershell
$jdk = 'C:/Program Files/Android/openjdk/jdk-21.0.8'
./scripts/dat/run-acceptance.ps1 -JavaHome $jdk -ReviewTests -TestSelector 'DatRedisIntegrationTest#objectIdAliasesMustShareProgressAndRanking'
./scripts/dat/run-acceptance.ps1 -JavaHome $jdk -ReviewTests -TestSelector 'DatRedisIntegrationTest#userIdAliasesShareProgressAndKeepAuthorization'
./scripts/dat/run-acceptance.ps1 -JavaHome $jdk -TestSelector 'DatRedisIntegrationTest,ProgressApiTest,RankingApiTest'
```

Chạy tuần tự; mỗi run tạo Mongo DB/Redis container/cổng và output riêng, giữ lại dữ liệu/evidence. Review test yêu cầu Redis rỗng nên chạy riêng từng method, không bật tất cả review vào cùng instance. Không flush DB13/14/15 đã có dữ liệu. Log *.log bị Git ignore; JSON/snapshot/fingerprint là evidence được đưa vào diff, không dựa vào log chưa track để kết luận duy nhất.

Fixture/benchmark độc lập dùng `scripts/dat/run-fixture.ps1`: Action seed/verify/benchmark, xem [README](../../scripts/dat/README.md). `verify` chỉ đọc DB; chọn output mới và copy manifest trước mỗi bộ kết quả cần giữ. Mongo `digital_library_dat_fixture_v1`, Redis DB0 prefix `dat-fixture:v1:` khác key API production; fixture không tự xuất hiện trên UI/API. Khi nhận manifest Sơn, tool chỉ đọc sourceDatabase của Sơn, ghi baseline vào DB fixture và Hash/ZSET vào namespace fixture riêng. Chưa được coi là seed demo chung.

## Alias cũ và migration chưa thực hiện

[Inventory verified](evidence/id-fix/legacy-inventory-verified.json): SCAN DB0..15 ở ba container cũ của repo,141 dòng,2 alias; một cặp Hash và một cặp member xung đột trong review DB0. Hash chuẩn page10 và alias page30; ranking score1+1. Không sửa/xóa/gộp dữ liệu đó. Bản inventory đầu lỗi grouping giữ để chẩn đoán, không dùng kết luận.

Code chỉ ngăn phân mảnh cho ghi mới: GET legacy progress vẫn đọc key chuẩn (có thể page10), GET ranking chỉ chuẩn hóa DTO (có thể hai entry cùng ID). Chưa có migration apply. [Phương án đề xuất](ID_NORMALIZATION.md): ranking cộng score bảo toàn lượt; progress chọn toàn bản updatedAt UTC mới nhất; timestamp hòa nhưng vị trí khác hoặc dữ liệu/TTL sai thì chặn xử lý thủ công. Cần duyệt phạm vi/quy tắc, backup/dry-run/CAS và ledger chống cộng lần hai trước mọi apply. Không coi migration là được duyệt qua tài liệu bàn giao này.

## Việc Sơn cần làm và điều kiện gỡ blocker

1. Cung cấp manifest nguồn thật: sourceDatabase,bookId,userId,chapter hợp lệ,page,line,score; ít nhất50 cặp progress và đúng50 sách. Đối chiếu Mongo và phối hợp seed có ownership; không dùng namespace fixture thay key demo production hoặc reset lượt đọc hiện có.
2. Bổ sung client Bearer cho GET/PUT progress; lấy userId từ phiên đăng nhập. Chốt cách phân trang và lưu khi chuyển trang/chương; xử lý401/403/404. Chỉ tự mở trang đầu khi chưa có progress và sách/chương đã tải hợp lệ.
3. Kiểm chứng flush request khi đóng tab; không mặc định sendBeacon dùng được PUT+Bearer. Đóng/mở lại cùng tài khoản phải phục hồi trang30, lưu HTTP/Hash/UI trước-sau để gỡ I01.
4. Gọi POST read đúng sự kiện mở chương; ghép metadata BXH qua batch theo id, giữ thứ tự và bỏ sách mất; hiển thị ít hơnN nếu batch thiếu, không bịa metadata. Dữ liệu legacy cần xử lý riêng sau khi migration được duyệt.
5. Chạy luồng mở nhiều chương, đối chiếu API/ZSET/Insight và thứ hạng web để gỡ I02/R05 UI. Backend pass không thay cho các bằng chứng này.
6. Chọn tài khoản/sách nhóm cố định, tổng duyệt ít nhất2 lần và lưu log/video/ảnh; xác nhận Vũ nhận raw/summary để đưa báo cáo. Chưa gửi tin ngoài khi user chưa giao. Cập nhật cả members/DAT.md, ACCEPTANCE_RESULTS và PROGRESS khi có kết quả mới.

Tài liệu hiện tại tách backend/fixture đã đạt khỏi UI, manifest Sơn, migration legacy và tổng duyệt còn chờ. Không reset usage.
