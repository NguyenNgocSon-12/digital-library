# Rà soát độc lập phần Đạt — 22/10/2026 20:46 +07

Kết luận: chưa hoàn thành. Phát hiện hai lỗi chức năng có cùng nguyên nhân: dùng chuỗi ObjectId đầu vào làm định danh Redis thay vì một dạng chuẩn. Cập nhật 18 mục nghiệm thu thành **12 Đạt, 2 Chưa đạt, 4 Bị chặn**; P02 và R01 chuyển Chưa đạt. Các kết quả trước vẫn có giá trị trong các ca đã chạy, không chứng minh các biến thể ID này đúng.

## Phát hiện

### F01 — P1: một sách bị chia điểm và mất metadata BXH

Vị trí: `ranking/service/RankingService.java:24` truyền nguyên bookId vào `RankingRepository.increment`; repository dùng chuỗi đó làm member. `BookService.exists` dùng `new ObjectId(bookId)` nên chấp nhận cả dạng viết hoa/thường của cùng ID.

Tái hiện trên sách thật `6ada13b412584a28f386bfef`: POST read bằng dạng chuẩn và `6ADA13B412584A28F386BFEF` đều 200/score1. GET ranking trả hai member, mỗi member score1, thay vì một member score2. Batch chỉ nhận ID viết hoa trả `[]` dù sách còn tồn tại: member do Đạt phát sinh không ghép được metadata theo hợp đồng Sơn. POST công khai đúng D03; đây là lỗi đồng nhất dữ liệu, không phải yêu cầu thêm login hay chống spam.

Hướng sửa trong phần Đạt: chuẩn hóa ID hợp lệ trước khi dùng Redis và trả DTO, giữ lookup qua service công khai. Kiểm tra dữ liệu alias đã tồn tại và lập phương án gộp có kiểm soát trước khi sửa dữ liệu thật; không tự ZREM/reset điểm. Không cần đổi nghiệp vụ catalog để ngăn phần Đạt sinh member sai chuẩn.

### F02 — P2: cùng sách có hai tiến trình, khôi phục vị trí cũ

Vị trí: `reading/service/ProgressService.java:30,36` truyền nguyên userId/bookId vào repository; key ghép chuỗi phân biệt hoa/thường. PUT sách dạng chuẩn page10, sau đó PUT cùng sách dạng viết hoa page30 đều 200. GET dạng chuẩn trả page10; Redis có hai Hash riêng, cùng user và cùng sách Mongo. Vi phạm ghi đè một cặp và khôi phục lần lưu mới nhất (P02/DoD).

Hướng sửa: thống nhất định danh đọc/ghi key sau khi xác minh quyền và tồn tại; giữ `CurrentUser.canAccess` và lỗi 403 trước lookup. Rà thêm admin dùng userId viết hoa và GET/PUT chéo dạng ID; biến thể userId này chưa được chạy trong lượt này, không coi là lỗi phân quyền đã chứng minh. Với Hash alias cũ cần chính sách chọn vị trí theo updatedAt và xử lý xung đột, không tự xóa dữ liệu.

## Kiểm chứng

- Nền Git `4a0dd9b31fdc17601e2891f5acf28f69b4d98954`, nhánh `codex/dat-work-dossier`, working tree có mã Đạt chưa commit trước lượt rà soát. Không sửa production code, catalog/identity/frontend/scripts seed của Sơn.
- Test mới `DatRedisIntegrationTest#objectIdAliasesMustShareProgressAndRanking`, chỉ bật khi `DAT_INTEGRATION_TESTS=true` và `DAT_REVIEW_TESTS=true`; dùng MockMvc full context, login thật, Mongo/Redis thật, không mock domain. Một test chạy, thất bại ba assertion: page30 thực tế10; một member thực tế hai; score2 thực tế1. Test đỏ là bằng chứng lỗi còn mở, không phải lỗi môi trường.
- [Request/response và hai snapshot Redis](evidence/review/20261022204608/api-redis-evidence.json), [môi trường và checksum test](evidence/review/20261022204608/environment.json), [log](evidence/review/20261022204608/test.log). `completed=false` vì assertion thất bại; không ghi đè bằng chứng acceptance cũ. Tám response được ghi, không chứa token/header đăng nhập/mật khẩu.
- JDK21.0.8/Maven3.10.0 được kiểm tra trực tiếp; Java không nằm trên PATH, dùng JAVA_HOME theo HANDOFF. Lệnh Maven: `./mvnw.cmd -B '-Dtest=DatRedisIntegrationTest#objectIdAliasesMustShareProgressAndRanking' test` từ backend. Đặt DAT_ACCEPTANCE_OUTPUT vào thư mục mới; MONGO_URI trỏ database review riêng và REDIS_URL trỏ Redis container mới/rỗng. Không chạy test này vào Redis đã có ranking.
- Mongo database riêng `digital_library_dat_review_20261022204608`; Redis container riêng `dl_dat_review_20261022204608`, cổng xem environment.json. Giữ container/data để kiểm tra, không FLUSH hoặc sửa dữ liệu cũ. Test này không cần chạy lại benchmark/seed hoặc bộ test cũ không đổi.
- Đối chiếu toàn bộ 14 checksum trong `evidence/acceptance/artifact-checksums.json`: đều khớp. Đây là kiểm tra tính nguyên vẹn artifact, không phải chạy lại nghiệm thu hoặc xác nhận toàn bộ trạng thái DB hiện tại. Script acceptance cũ chỉ hash nguồn test; chưa có fingerprint toàn bộ production code để ràng buộc tuyệt đối bằng chứng với working tree.

## Khoảng trống còn lại

| Mục | Trạng thái và bước kiểm chứng tiếp |
|---|---|
| P02 / R01 | Chưa đạt do F02/F01. Sửa đồng nhất ID rồi chạy regression trong môi trường mới; xác minh một Hash/một member, điểm2, GET page30 và batch trả metadata. Sau sửa mới chạy lại bộ test liên quan. |
| P03 phân quyền | Ca login thật/401/403/admin trước có bằng chứng; code vẫn gắn Authenticated, kiểm quyền trước lookup/Redis. Không phát hiện bypass trong phần đã đọc; chưa chứng minh biến thể ID user/admin, logout/expired token riêng với progress ở lượt này. |
| R05 / I01 / I02 | Bị chặn: ReadingPage/RankingPage vẫn placeholder khi đọc nguồn hiện tại. Chưa có browser lưu khi đóng tab, khôi phục trang30, tăng điểm/thứ hạng trên web hoặc bỏ sách đã xóa. Cần Sơn tích hợp theo SHARED rồi cung cấp request/Redis/UI trước-sau. |
| Seed dữ liệu nhóm | S01/S02 chỉ đạt fixture riêng. Chưa có manifest Sơn; chưa chứng minh key chuẩn `progress:*`/`ranking:books` chứa bộ seed dùng demo nhóm. Nhận manifest rồi đối chiếu Mongo/user/chapter, phối hợp seed có ownership; không dùng fixture namespace thay dữ liệu API. |
| B01 / I03 | B01 có raw/summary local fixture; chưa có bằng chứng Vũ nhận số liệu và hai lần tổng duyệt với nhóm. Không tự gửi thông báo. |
| D06 / vận hành | Cleanup sách/user chưa chốt; vẫn có thể giữ member mồ côi/làm Top N sau ghép ngắn hơn N. Đây là giới hạn đã công bố, không tự nâng thành lỗi chống hợp đồng. Hỏng Hash/WRONGTYPE, Redis mất kết nối, race xóa sách giữa lookup và ghi chưa có ca nghiệm thu riêng. |
| Git / bàn giao | members/DAT.md vẫn toàn checkbox trống; hồ sơ có kết quả chi tiết nhưng chưa đồng bộ checklist gốc. Giữ trống các mục tích hợp chưa đạt; trước PR phải đối chiếu lại remote develop và có reviewer. Không fetch/merge/push/PR trong lượt review này. |

Thứ tự xử lý: F01/F02 → regression và kiểm tra dữ liệu alias → phối hợp manifest/UI Sơn → hai lần demo và bàn giao số liệu Vũ. Các mục optional (danh sách progress, dedupe) không bị coi là thiếu bắt buộc. Không thay các quyết định D01–D08 đã xác nhận.
