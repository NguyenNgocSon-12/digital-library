# Bàn giao theo hai PR — bản nháp, chưa tạo PR

Ngày22/10/2026. Remote origin `https://github.com/ThaiDuyVu/digital-library.git` đã fetch; main4a0dd9b,develop5b1bec0. main...develop=5/0. Commit Đạt giữ nguyên `c17086df35a7490770c0c8a3df2dc612ef8e42df` trên codex/dat-work-dossier. README mục7 yêu cầu PR vào develop và ít nhất1 reviewer. Tài liệu này không cho phép tự cập nhật nhánh chung,push hoặc gửi PR.

## PR1 — main → develop: nền catalog/auth/service

- Base: develop; compare: main (remote main đã có nền,không dùng nhánh Đạt làm head PR này).
- Title: `chore: sync catalog and authentication foundation into develop`.
- Phạm vi hiện tại:5 commit/50 đường dẫn,không có commit c17086d hoặc69 file phần Đạt. Rà lại remote/diff trước khi gửi vì số liệu có thể thay đổi.

Nội dung PR1 soạn sẵn:

```markdown
Đồng bộ nền backend/catalog/identity đang có trên main sang develop trước khi tích hợp reading/ranking của Đạt. develop hiện là tổ tiên của main và thiếu5 commit sau:

| Commit | Nội dung | Phụ thuộc mà reading/ranking cần |
|---|---|---|
| 6d6cfe7 | Sửa spring.mongodb.uri và thêm xử lý lỗi chung | ApiException/GlobalExceptionHandler và cấu hình Mongo đúng nền |
| 2650dda | Tài khoản độc giả và Redis-backed login sessions | Authenticated,CurrentUser.canAccess,UserService,AuthInterceptor/resolver và phiên Bearer |
| 65ab069 | CRUD sách/chương MongoDB | BookService.exists/getChapter và API metadata batch dùng ghép ranking |
| 6ef26a9 | Kiến trúc,schema và hợp đồng API | Quy ước ID,Hash/ZSET,auth,domain ownership và tích hợp dùng chung |
| 4a0dd9b | Merge PR#2 vào main | Điểm nền đã tích hợp của bốn commit trên; không phải một tính năng Redis bổ sung |

PR này chỉ đưa nền có sẵn trên main về develop,không triển khai reading/ranking và không kèm commit Đạt. Diff hiện tại50 file bao gồm catalog,identity,common,schema/config và tài liệu nguồn.

Đạt gọi BookService qua service công khai để kiểm sách/chương; progress dùng Authenticated/CurrentUser.canAccess và UserService cho admin target; lỗi theo ApiException. Cherry-pick riêng phần Đạt vào develop cũ sẽ thiếu các hợp đồng này,không tạo ra một PR chức năng độc lập hợp lệ.

Đề nghị maintainer/Vũ review nền trước,ít nhất1 reviewer theo quy ước repo. Ưu tiên merge commit hoặc fast-forward được maintainer chấp thuận để giữ main4a0dd9b trong ancestry của develop. Không squash/rebase PR nền nếu muốn giữ nguyên nhánh/commit Đạt và PR2 chỉ hiện đúng một commit. Nếu bắt buộc squash/rebase,cần xử lý ancestry PR2 riêng sau đó.

Không chạy lại test trong bước soạn PR vì mã/phụ thuộc không đổi; không coi git diff hoặc build là kiểm chứng chức năng mới. Các evidence Mongo/Redis của Đạt trên nền4a0dd9b được bàn giao riêng ở docs/dat/ID_NORMALIZATION.md,sẽ được thêm trong PR2. Chưa có kết luận review mới về toàn bộ CRUD/auth của Vũ từ bước soạn PR này.

Không migration dữ liệu,không reset Redis,không thay blocker UI/manifest/tổng duyệt. Chỉ sau khi nền đã merge mới kiểm tra lại PR Đạt so với develop.
```

Lưu ý: links docs/dat của Đạt chưa có trên main trước PR2; reviewer dùng artifact bàn giao/workspace hiện tại,không giả định PR1 đã chứa những file đó. Nếu GitHub không cho merge commit,nhóm cần chốt cách giữ ancestry hoặc phương án tạo nhánh tích hợp mới,không tự đổi cài đặt repo.

## PR2 — nhánh Đạt → develop sau PR1

- Giữ commit c17086d; không amend/rebase/cherry-pick ở lượt chuẩn bị này.
- Title: `feat: add Redis reading progress and book ranking with canonical ObjectIds`.
- Dùng [body đầy đủ đã soạn](COMMIT_PR_DRAFT.md),cập nhật base develop và SHA sau gate bên dưới.
- [Rà toàn bộ69 file](COMMIT_SCOPE_AUDIT.md):10 nghiệp vụ,4 test,4 script,51 tài liệu/bằng chứng. Không có file nghiệp vụ Vũ/Sơn,secret hoặc runtime data tạm. Artifact nghiệm thu được chọn là dữ liệu cố định dùng truy vết/tái lập,không phải dữ liệu nhóm đã tích hợp.

Đoạn mở đầu PR2 sau gate:

```markdown
PR nền main→develop đã được merge và xác minh chứa ancestry4a0dd9b. PR này chỉ thêm commit c17086d của Đạt: reading progress Hash,atomic book ranking ZSET và chuẩn hóa ObjectId đọc/ghi/DTO. Diff69 file đã được phân loại và review; không chứa5 commit nền Vũ trong danh sách commit của PR.

Hai regression Mongo/Redis/login thật đã qua; bộ liên quan23 ca qua,0 lỗi,2 review ca đã chạy riêng nên skip trong run chung. Fixture50 Hash/50 sách,benchmark raw/summary và ảnh Insight có evidence. Không chạy lại test không đổi chỉ để làm mới ngày kiểm chứng.

Backend/fixture đạt tách biệt R05 UI,I01–I03,manifest Sơn và tổng duyệt còn chờ. Alias legacy giữ nguyên; migration chỉ có đề xuất,chưa được duyệt/chạy. Xem HANDOFF,ACCEPTANCE_RESULTS và ID_NORMALIZATION. Cần ít nhất1 reviewer; chưa coi hệ thống hoàn thành.
```

Không copy câu “PR nền đã merge” trước khi gate thật sự qua. PR2 hiện còn chặn bởi PR1 chưa được tạo/merge.

## Gate bắt buộc sau khi PR1 được merge

Các lệnh dưới là hướng dẫn cho lượt sau,không chạy như thao tác cập nhật nhánh trong lượt này:

```powershell
git fetch origin
git status --short --branch
git rev-parse codex/dat-work-dossier
# Phải vẫn là c17086df35a7490770c0c8a3df2dc612ef8e42df.
git merge-base --is-ancestor 4a0dd9b31fdc17601e2891f5acf28f69b4d98954 origin/develop
# Exit0: develop chứa ancestry nền; nếu khác0 thì dừng.
git log --oneline origin/develop..c17086d
# Chỉ một dòng c17086d; nếu rỗng thì Đạt đã được tích hợp,không tạo PR trùng.
git diff --name-status origin/develop...c17086d
git diff --check origin/develop...c17086d
# Đối chiếu đủ69 file/status với git diff --name-status c17086d^ c17086d.
git diff 4a0dd9b..origin/develop -- backend/pom.xml backend/src/main backend/src/main/resources
# Nếu service/auth/config/dependency thay đổi có liên quan,đánh giá và chỉ chạy lại nhóm test bị ảnh hưởng.
```

HEAD/working tree còn tài liệu chuẩn bị2PR chưa commit; chúng không nằm trong69 file của c17086d. Không đưa file untracked legacy-inventory.json vào stage/push. Chỉ dùng dữ liệu commit để xác minh diff PR,còn thay đổi tài liệu mới phải review/commit riêng nếu user giao; không âm thầm amend c17086d.

Nếu develop đã có main bằng merge commit nhưng thêm một merge node,develop có thể có commit riêng so với nhánh Đạt; đó không tự làm PR2 lẫn nền. Điều kiện là `develop..c17086d` chỉ có commit Đạt và three-dot diff chỉ có69 file đúng phạm vi.

Nếu PR1 squash/rebase làm mất ancestry4a0dd9b,gate dừng. Phương án dự phòng cần giao riêng: giữ c17086d/nhánh cũ nguyên vẹn,tạo nhánh cá nhân mới từ develop sau nền rồi cherry-pick duy nhất c17086d; SHA mới,review conflict/fingerprint/phụ thuộc trước khi push. Không thực hiện dự phòng trong lượt này.

Sau gate,việc push/tạo PR chỉ làm khi được người dùng giao tiếp. Không tự theo dõi lịch/automation hoặc cập nhật nhánh dùng chung. UI,manifest Sơn,tổng duyệt và migration legacy vẫn là blocker riêng. Không reset usage.
