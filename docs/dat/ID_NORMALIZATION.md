# Sửa F01/F02 và kiểm tra alias Redis — 22/10/2026

Đã sửa hai lỗi chức năng trong [review độc lập](INDEPENDENT_REVIEW.md), kiểm chứng bằng login thật và Mongo/Redis thật. Nền Git `4a0dd9b`, nhánh `codex/dat-work-dossier`, working tree chưa commit. Không sửa catalog/identity/common hoặc hợp đồng status/error.

## Thay đổi và kết quả

ProgressService chuẩn hóa mọi userId/bookId hợp lệ bằng `ObjectId.toHexString()` trước kiểm quyền, lookup và GET/PUT Redis. Vẫn gọi `CurrentUser.canAccess`, kiểm quyền trước lookup; ID sai giữ nguyên để service trả lỗi theo thứ tự cũ. RankingService chuẩn hóa trước exists/ZINCRBY và chuẩn hóa bookId của DTO GET ranking. Không tự ghi lại member/Hash legacy khi đọc.

| Kiểm chứng | Actual | Bằng chứng |
|---|---|---|
| F01/R01 | POST dạng thường + hoa đều200, trả ID chuẩn; chỉ một member score2; batch với ID lấy từ ranking trả một metadata đúng sách | [run F01/F02](evidence/acceptance/20261022205242_361ca5b9/api-redis-evidence.json) |
| F02/P02 | PUT chuẩn page10 rồi PUT alias page30; GET chuẩn và hoa cùng page30, không tạo Hash alias | Cùng run trên, snapshot canonical/alias; `completed=true` |
| userId hoa, chính chủ/admin | Chính chủ PUT userId/bookId hoa page30 rồi GET chuẩn30; admin cập nhật alias page42, chính chủ GET hoa42. Bốn biến thể key chỉ có key chuẩn tồn tại | [run userId/auth](evidence/acceptance/20261022205402_142d850b/api-redis-evidence.json) |
| Quyền và ID sai | User khác GET/PUT403, Hash không đổi; userId sai: chính chủ403/admin404; bookId sai404. Bộ liên quan kiểm lại book/user mất, JSON sai,401/403/404 | Run userId/auth và [bộ liên quan](evidence/acceptance/20261022205450_1860e247/api-redis-evidence.json) |
| Đọc member legacy | DTO trả ID chuẩn, score7; member viết hoa và score7 vẫn nguyên, không có member chuẩn tự sinh | Run userId/auth; legacy chỉ được tạo trong Redis fixture mới của test |
| Bộ P/R liên quan | 23 ca qua,0 lỗi;2 review test skip trong run chung vì mỗi ca yêu cầu Redis rỗng và đã chạy riêng thành công. Bao gồm concurrency40/40,top12→10,hòa điểm,deleted book/batch và validation/auth | Run liên quan, `test.log` và snapshot/assertion |

Hai run regression mỗi run1 test qua, không skip. Đây là assertion chức năng với database thực, không phải kết luận từ build. Từng thư mục có `environment.json`, checksum nguồn test và `production-checksums.json` cho toàn bộ Java production. Dữ liệu/container test được giữ riêng, không flush DB cũ. Bằng chứng đỏ review20:46 và các lần seed/benchmark trước được giữ nguyên.

## Dữ liệu cũ — chỉ kiểm kê, chưa migration

[Inventory đã xác minh](evidence/id-fix/legacy-inventory-verified.json): SCAN các DB0..15 của đúng ba container cũ `dl_redis`, `dl_dat_acceptance_20261022203530_82c03582`, `dl_dat_review_20261022204608`; đọc key progress/ranking kể cả namespace fixture, không đọc giá trị session. Tổng141 dòng (Hash hoặc member),2 dòng alias;1 nhóm Hash xung đột và1 nhóm ranking xung đột, đều ở container review/DB0. Không phát hiện alias trong hai container cũ còn lại trong phạm vi scan. Không kiểm kê container Học Liệu Số/Neo4j. Các container regression mới không nằm trong inventory lịch sử; một alias score7 trong run userId là fixture cố ý để thử read DTO.

Nhóm thực tế trong review:

- User `6ada13b412584a28f386bfee`, sách `6ada13b412584a28f386bfef`: Hash chuẩn page10, updatedAt `2026-10-22T13:46:28.701206300Z`; Hash bookId hoa page30, updatedAt `2026-10-22T13:46:28.717022Z`.
- ZSET `ranking:books`: member sách chuẩn score1 và member sách hoa score1.

Chưa thay đổi hai Hash/member này. Sau sửa, GET progress định tuyến key chuẩn nên dữ liệu cũ vẫn có thể trả page10 cho tới khi migration được duyệt. GET ranking chuẩn hóa ID DTO nhưng chưa cộng điểm hay loại member trùng; dữ liệu legacy có thể vẫn trả hai entry cùng ID chuẩn. Code ngăn phân mảnh cho ghi mới, không thay thế migration.

`legacy-inventory.json` là bản chẩn đoán đầu: nhóm xung đột dùng Group-Object sai trên Hashtable nên không được dùng làm kết luận. Script đã sửa group bằng khóa container/DB/canonical rõ ràng rồi chạy lại thành `legacy-inventory-verified.json`; rows gốc đều được giữ. Báo cáo này chỉ dựa bản verified.

## Phương án migration đề xuất — cần chốt trước khi chạy

1. Chọn chính xác instance/DB/namespace và thời gian dừng ghi cho progress/ranking. Sao lưu dữ liệu/TTL và checksum; chạy dry-run tạo manifest nhóm alias cùng expected-before/after. ID sai định dạng hoặc sai TYPE giữ nguyên, tách hàng cần xử lý; không đoán ID.
2. Ranking: gom các member hợp lệ có cùng ObjectId chuẩn; đề xuất **cộng tất cả score** để bảo toàn lượt đã đếm theo D03 (không dedupe retroactive). Ví dụ review1+1→2. Score phải hữu hạn, không âm, nguyên và nằm trong biên chính xác an toàn; dữ liệu sai phải dừng nhóm đó, không ép kiểu/làm tròn.
3. Progress: chọn **toàn bộ bốn field của bản có updatedAt UTC hợp lệ mới nhất**, không lấy trang lớn nhất hoặc trộn field. Ví dụ review chọn page30. Hòa timestamp và vị trí giống nhau: tương đương; hòa timestamp nhưng vị trí khác, thiếu/sai field/timestamp hoặc TTL bất thường: chặn nhóm đó để người phụ trách chọn, không ưu tiên key chuẩn tùy tiện.
4. Chỉ áp dụng sau xác nhận quy tắc trên. Kiểm tra CAS/WATCH hoặc Lua với before snapshot trong từng nhóm để không ghi đè dữ liệu mới; nhóm thay đổi sau dry-run phải tính lại và xin xử lý xung đột. Sau backup và duyệt mới ghi canonical, xác minh rồi mới loại alias; không tự ZREM/DEL ở lượt này. Session và key ngoài manifest không thuộc phạm vi.
5. Có ledger/checksum để chạy lại không cộng điểm lần hai; ghi absolute expected score và đánh dấu nhóm hoàn thành cùng transaction thay vì ZINCRBY phần tổng lặp lại. Dry-run lần hai phải không còn việc cho nhóm đã hoàn thành. Nếu cần rollback, dừng ghi và đối chiếu before/after; không phục hồi đè lượt đọc mới phát sinh.

Chính sách này là đề xuất, **chưa được thực thi hoặc coi là đã được duyệt**. Giữ blocker migration dữ liệu cũ riêng với UI, manifest Sơn và tổng duyệt. Không cần chạy lại benchmark vì hot path phép đo fixture độc lập không thay đổi.

## Tái lập

```powershell
$jdk = 'C:/Program Files/Android/openjdk/jdk-21.0.8'
./scripts/dat/run-acceptance.ps1 -JavaHome $jdk -ReviewTests -TestSelector 'DatRedisIntegrationTest#objectIdAliasesMustShareProgressAndRanking'
./scripts/dat/run-acceptance.ps1 -JavaHome $jdk -ReviewTests -TestSelector 'DatRedisIntegrationTest#userIdAliasesShareProgressAndKeepAuthorization'
./scripts/dat/run-acceptance.ps1 -JavaHome $jdk -TestSelector 'DatRedisIntegrationTest,ProgressApiTest,RankingApiTest'
./scripts/dat/audit-id-aliases.ps1 -Output C:/path/new-legacy-inventory.json
```

Chạy tuần tự. Script tạo DB/container riêng cho mỗi run và lưu fingerprint production; không bật mọi review test cùng lúc vào cùng Redis vì chúng cần môi trường rỗng. Inventory chỉ dùng SCAN/TYPE/HGETALL/ZRANGE, từ chối ghi đè file bằng chứng có sẵn. Không có script apply migration.
