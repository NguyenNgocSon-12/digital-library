# Hướng dẫn làm việc phần Đạt

## Đọc trước khi làm

Đọc `README.md`, `members/DAT.md`, `docs/SHARED.md`, `docs/ARCHITECTURE.md`, `docs/PLAN.md`, `docs/DEMO_SCRIPT.md` và `docs/dat/` trước khi thay đổi. Kiểm tra Git và mã nguồn thực tế; checkbox trong tài liệu không thay bằng chứng kiểm thử.

Nguồn phân công chung vẫn nằm ở `members/` và `docs/SHARED.md`. Hồ sơ `docs/dat/` diễn giải việc thực hiện, không tự thay hợp đồng nhóm. Khi nguồn mâu thuẫn, ghi rõ vào `docs/dat/DECISIONS.md` và đối chiếu code.

## Phạm vi

- Đạt sở hữu `backend/src/main/java/vn/edu/huit/digitallibrary/reading/`, `ranking/` và kiểm thử tương ứng trong `backend/src/test/java/`.
- Vũ sở hữu `catalog/`, `identity/`, `docs/ARCHITECTURE.md`; Sơn sở hữu `frontend/src/features/`, `scripts/seed/`. Seed Redis phải phối hợp Sơn, dùng ID thật từ MongoDB.
- Không truy cập repository của domain khác; dùng service công khai, DTO. Kiểm tra sách qua `BookService.exists(bookId)`; không sao chép document sách vào Redis.
- `common/`, cấu hình gốc, `frontend/src/shared/`, hợp đồng API là phần dùng chung: mô tả lý do, ảnh hưởng trong PR và báo nhóm theo `docs/SHARED.md`. Không gửi thông báo ra ngoài khi chưa được người dùng giao.
- Không sửa nghiệp vụ ngoài phần Đạt, không đổi/xóa nguồn, không ghi đè thay đổi của người khác.

## Giới hạn hiện tại

Ngày 22/10/2026 người dùng đã giao triển khai reading/ranking và xác nhận D01–D05; sau đó cho phép fixture/seed/benchmark độc lập với database Mongo và namespace Redis riêng. Không sửa dữ liệu hiện có. Tích hợp UI/dữ liệu Sơn vẫn chờ phối hợp. Không sử dụng lượt reset usage. Làm tuần tự, không tự mở chat hoặc chạy nhiều agent; khi ngắt quãng, lưu checkpoint vào `docs/dat/PROGRESS.md`.

## Quy ước triển khai sau khi được giao

- Progress: Hash `progress:{userId}:{bookId}`, `chapter>=1`, `page>=1`, `line>=0`, `updatedAt` ISO 8601 UTC; chưa đặt TTL trong demo.
- Ranking: ZSET `ranking:books`, member=`bookId`, score=lượt mở chương; dùng phép tăng nguyên tử, không đọc rồi cộng trong Java.
- Progress dùng `@Authenticated`, `CurrentUser.canAccess(userId)`; không tin userId trên URL. Dùng `ApiException` và lỗi `{code,message}` có sẵn.
- Không tự chốt nghiệp vụ còn thiếu trong DECISIONS. Phân biệt tùy chọn với bắt buộc.
- Không dùng FLUSHDB/FLUSHALL hoặc `docker compose down -v`; không commit `.env`, token, mật khẩu thật.
- Git chung: nhánh riêng → PR vào `develop`, ít nhất một người review; kiểm tra độ lệch `main/develop` trước khi tạo PR. Nhánh hồ sơ hiện tại xuất phát từ main vì develop thiếu nền tảng mới.

## Kiểm tra và bàn giao

Tại gốc repo: `git status --short`, `git branch -avv`, `git diff --check`. Trên Windows, backend dùng `cd backend` rồi `.\mvnw.cmd test`; cần JDK phù hợp và Mongo/Redis cho context/integration test. Kiểm tra `java -version`, `.\mvnw.cmd -v` trước. Không coi wrapper là JDK có sẵn.

Khi được giao chạy hệ thống: xem `docs/dat/HANDOFF.md`; `.env` chỉ được Compose tự nạp, Spring Boot cần biến môi trường tương ứng. Không sửa dependency/cài công cụ toàn máy chỉ để bỏ qua lỗi khi chưa xác định nguyên nhân.

Sau mỗi mốc, ghi commit nền, lệnh chạy, kết quả, dữ liệu kiểm thử, bằng chứng, blocker và bước kế tiếp vào PROGRESS. Kết luận dùng Đạt / Chưa đạt / Bị chặn / Chưa thực hiện. Build hoặc mock test không chứng minh Redis thực tế hay luồng giao diện. Không lặp kiểm tra nếu bằng chứng còn phù hợp và code/môi trường liên quan chưa đổi.

## Đồng bộ tiến độ với phân công gốc

Sau mỗi mốc đã sửa và kiểm chứng, đồng bộ `members/DAT.md` cùng `docs/dat/PROGRESS.md` và nghiệm thu. Chỉ đánh dấu `[x]` khi toàn bộ công việc ở dòng đó có bằng chứng đạt; mục chưa đạt, bị chặn hoặc tùy chọn chưa làm giữ `[ ]`, ghi ngắn lý do và dẫn tới bằng chứng `docs/dat/`. Phân biệt fixture riêng đã kiểm chứng với tích hợp manifest/dữ liệu Sơn, UI và tổng duyệt chưa hoàn thành. Không đổi nội dung hay người phụ trách trong phân công gốc; có thể thêm ghi chú trạng thái sau dòng nhiệm vụ. Khi review phát hiện lỗi, cập nhật lại checkbox liên quan theo bằng chứng hiện tại.
