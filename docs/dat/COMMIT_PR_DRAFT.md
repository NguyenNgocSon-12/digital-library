# Bản nháp commit và PR phần Đạt

Chỉ soạn nội dung, chưa stage/commit/push hoặc tạo PR. Quy ước: Conventional Commit; nhánh riêng → PR vào develop; ít nhất1 reviewer. Nhánh hiện tại codex/dat-work-dossier từ main4a0dd9b, develop thiếu5 commit nền sau fetch22/10/2026. Không mở PR vào develop cũ vì diff kéo catalog/identity của Vũ; cần thống nhất nền trước, không tự merge nhánh chung.

## Commit đề xuất

Một commit chức năng đầy đủ, gồm mã/test/tools và hồ sơ liên quan trong scope đã giao:

```text
feat: implement Redis reading progress and book ranking

Add authenticated progress Hash APIs and public atomic ranking APIs.
Canonicalize valid ObjectIds for progress reads/writes and ranking IDs;
retain existing authorization and invalid-ID error behavior.

Add isolated fixtures, repeatable real Mongo/Redis acceptance runs,
raw benchmark samples and regression evidence for ObjectId aliases.
Document API contracts, integration blockers and the pending legacy
migration; synchronize Dat's checklist without changing assignments.
```

Không dùng riêng `fix:` cho toàn diff vì reading/ranking còn chưa có trong HEAD. Nếu tách commit sau khi thống nhất nền, dùng feat cho backend, test cho tools/evidence, docs cho contract/handoff; không cherry-pick thiếu phần phụ thuộc.

Scope để xem trước trước khi stage: reading/,ranking/; test tương ứng; scripts/dat/; AGENTS.md; docs/dat/; docs/SHARED.md; members/DAT.md. Không dùng `git add .` mà chưa đối chiếu danh sách cuối. Không đưa .env,*.log,target/,token/mật khẩu hoặc thay đổi ngoài scope vào commit. Các file evidence lịch sử/diagnostic có ghi rõ trạng thái, không dùng log ignored làm bằng chứng duy nhất.

## PR title

```text
feat: add Redis reading progress and book ranking with canonical ObjectIds
```

## PR body soạn sẵn

```markdown
Tiến trình đọc và BXH chưa có triển khai trên nền repo. Thay đổi này thêm GET/PUT progress bằng Redis Hash và API tăng lượt đọc/Top N bằng Redis ZSET. Progress yêu cầu Bearer token và quyền chính chủ/admin; ranking công khai theo D01–D05 đã xác nhận.

ID Mongo hoa/thường được chuẩn hóa về ObjectId hex thường trước tạo key/member và trả bookId. Ví dụ PUT sách dạng hoa trang30 rồi GET dạng chuẩn trả30; POST cùng sách dạng hoa/thường tăng vào một member score2 và ghép metadata qua batch được. Không sửa catalog/identity hoặc tự migration alias đã tồn tại.

### Phạm vi và contract dùng chung

- Thêm reading/ranking và test; tools fixture/benchmark độc lập được giao ở scripts/dat.
- docs/SHARED công bố response/status, giới hạn top1–100, quyền và invariant ID để Sơn tích hợp; không đổi DTO catalog/auth.
- members/DAT, AGENTS và docs/dat đồng bộ tiến độ/bằng chứng. Không thay phân công gốc, frontend hoặc scripts/seed của Sơn.

### Kiểm chứng

- Hai regression Mongo/Redis/login thật: mỗi run1 test qua, không skip; xác minh ID hoa/thường cùng progress/member, metadata và quyền chính chủ/admin.
- Bộ P/R liên quan:23 ca qua,0 lỗi;2 review test skip trong run chung vì đã chạy riêng trên Redis mới. Có40 request đồng thời,top mặc định trên12 sách,validation/auth và deleted-book/batch.
- Fixture riêng:50 Hash/50 sách Mongo thật,rerun reset riêng fixture và sentinel được bảo toàn; Redis Insight có ảnh Hash/ZSET/session TYPE.
- Benchmark:200 warm-up/backend,1000 mẫu/backend,concurrency1,0 lỗi; CSV và summary mean/median/p95 có phép tính độc lập. Kết quả chỉ áp dụng lần đo local, không phải SLA.
- Evidence và production fingerprints: docs/dat/ID_NORMALIZATION.md và docs/dat/ACCEPTANCE_RESULTS.md. Cách chạy: docs/dat/HANDOFF.md và scripts/dat/README.md.

### Giới hạn cần review

- Bảng nghiệm thu hiện tại14 Đạt/0 Chưa đạt/4 Bị chặn trong phạm vi đã kiểm chứng; chưa hoàn thành hệ thống.
- R05 UI và I01–I03 chờ Sơn tích hợp,manifest dữ liệu nhóm,hai lần tổng duyệt và xác nhận Vũ nhận số liệu. Seed/benchmark đã đạt chỉ trên fixture riêng.
- Migration alias legacy chưa chạy. Hai Hash/members cũ còn nguyên; GET progress có thể thấy bản chuẩn cũ và GET ranking có thể có hai entry cùng ID chuẩn. Quy tắc migration chỉ là đề xuất cần duyệt riêng.
- Danh sách progress theo user,dedupe và cleanup sách/user chưa triển khai/chưa chốt, không tự nâng thành yêu cầu bắt buộc.
```

Trước khi dùng bản nháp: kiểm tra lại base develop và diff thực tế sau giải quyết nền; cần ít nhất1 review. Bản này chưa được gửi đến GitHub hoặc thành viên nhóm. Không reset usage.
