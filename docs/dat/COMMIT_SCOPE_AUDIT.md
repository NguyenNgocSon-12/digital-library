# Rà 69 file của commit c17086d

Đối tượng rà là tree/diff immutable của c17086df35a7490770c0c8a3df2dc612ef8e42df so với parent4a0dd9b, không phải mọi file hiện có trong workspace. Commit được giữ nguyên, không amend/rebase/cherry-pick.

| Nhóm | Số file |
|---|---:|
| Mã nghiệp vụ | 10 |
| Kiểm thử | 4 |
| Script | 4 |
| Tài liệu và bằng chứng | 51 |

Cả69 đường dẫn đều thuộc phạm vi Đạt hoặc tài liệu chung được giao cập nhật. Không có catalog/identity/common/frontend/scripts/seed,dependency hoặc cấu hình gốc trong diff Đạt. docs/SHARED chỉ công bố contract; members/DAT giữ nhãn13 nhiệm vụ và ghi tiến độ; AGENTS bổ sung quy tắc đồng bộ.

51 tài liệu/bằng chứng gồm hồ sơ Markdown,regression request/response đã bỏ Authorization/login credentials,checksum nguồn,fixture manifest được dùng để tái lập,CSV benchmark/summary,PNG Insight và inventory verified phục vụ quyết định migration. Đây là artifact nghiệm thu có chủ đích, không phải collection dump hoặc runtime Redis/Mongo data. Dữ liệu fixture không được trình bày là dữ liệu Sơn.

Không có .env,log,target,node_modules,RDB/AOF hoặc bản inventory chẩn đoán sai trong tree commit. legacy-inventory.json vẫn là file local untracked, không bị xóa. Password fixture/default demo trong code là dữ liệu mẫu công khai của luồng kiểm thử, không phải credential thật. Quét mẫu token/private key không có kết quả; ảnh Insight chỉ chứa fixture IDs/score/Hash và TYPE session, không có token hoặc giá trị session.

## Mã nghiệp vụ
```text
backend/src/main/java/vn/edu/huit/digitallibrary/ranking/controller/RankingController.java
backend/src/main/java/vn/edu/huit/digitallibrary/ranking/dto/RankingEntry.java
backend/src/main/java/vn/edu/huit/digitallibrary/ranking/repository/RankingRepository.java
backend/src/main/java/vn/edu/huit/digitallibrary/ranking/service/RankingService.java
backend/src/main/java/vn/edu/huit/digitallibrary/reading/controller/ProgressController.java
backend/src/main/java/vn/edu/huit/digitallibrary/reading/dto/ProgressIntegerDeserializer.java
backend/src/main/java/vn/edu/huit/digitallibrary/reading/dto/ProgressRequest.java
backend/src/main/java/vn/edu/huit/digitallibrary/reading/dto/ProgressResponse.java
backend/src/main/java/vn/edu/huit/digitallibrary/reading/repository/ProgressRepository.java
backend/src/main/java/vn/edu/huit/digitallibrary/reading/service/ProgressService.java
```

## Kiểm thử
```text
backend/src/test/java/vn/edu/huit/digitallibrary/ranking/RankingApiTest.java
backend/src/test/java/vn/edu/huit/digitallibrary/reading/DatFixtureToolTest.java
backend/src/test/java/vn/edu/huit/digitallibrary/reading/DatRedisIntegrationTest.java
backend/src/test/java/vn/edu/huit/digitallibrary/reading/ProgressApiTest.java
```

## Script
```text
scripts/dat/README.md
scripts/dat/audit-id-aliases.ps1
scripts/dat/run-acceptance.ps1
scripts/dat/run-fixture.ps1
```

## Tài liệu và bằng chứng
```text
AGENTS.md
docs/SHARED.md
docs/dat/ACCEPTANCE.md
docs/dat/ACCEPTANCE_RESULTS.md
docs/dat/COMMIT_PR_DRAFT.md
docs/dat/DECISIONS.md
docs/dat/FINAL_REVIEW.md
docs/dat/HANDOFF.md
docs/dat/ID_NORMALIZATION.md
docs/dat/INDEPENDENT_REVIEW.md
docs/dat/PLAN.md
docs/dat/PROGRESS.md
docs/dat/RESULTS.md
docs/dat/evidence/acceptance/20261022203530_82c03582/api-redis-evidence.json
docs/dat/evidence/acceptance/20261022203530_82c03582/environment.json
docs/dat/evidence/acceptance/20261022205242_361ca5b9/api-redis-evidence.json
docs/dat/evidence/acceptance/20261022205242_361ca5b9/environment.json
docs/dat/evidence/acceptance/20261022205242_361ca5b9/production-checksums.json
docs/dat/evidence/acceptance/20261022205402_142d850b/api-redis-evidence.json
docs/dat/evidence/acceptance/20261022205402_142d850b/environment.json
docs/dat/evidence/acceptance/20261022205402_142d850b/production-checksums.json
docs/dat/evidence/acceptance/20261022205450_1860e247/api-redis-evidence.json
docs/dat/evidence/acceptance/20261022205450_1860e247/environment.json
docs/dat/evidence/acceptance/20261022205450_1860e247/production-checksums.json
docs/dat/evidence/acceptance/api-redis-evidence.json
docs/dat/evidence/acceptance/artifact-checksums.json
docs/dat/evidence/acceptance/benchmark/benchmark-raw.csv
docs/dat/evidence/acceptance/benchmark/benchmark-summary.json
docs/dat/evidence/acceptance/benchmark/fixture-audit.json
docs/dat/evidence/acceptance/benchmark/manifest.json
docs/dat/evidence/acceptance/benchmark/raw-summary-check.json
docs/dat/evidence/acceptance/benchmark/run-environment.json
docs/dat/evidence/acceptance/redis-insight-hash.png
docs/dat/evidence/acceptance/redis-insight-ranking.png
docs/dat/evidence/acceptance/redis-insight-session-type.png
docs/dat/evidence/acceptance/redis-insight-state.txt
docs/dat/evidence/acceptance/redis-insight-types-state.txt
docs/dat/evidence/api-tests.txt
docs/dat/evidence/fixture/benchmark-raw.csv
docs/dat/evidence/fixture/benchmark-summary.json
docs/dat/evidence/fixture/cpu.json
docs/dat/evidence/fixture/manifest.json
docs/dat/evidence/fixture/memory.json
docs/dat/evidence/fixture/redis-command.json
docs/dat/evidence/fixture/redis-version.txt
docs/dat/evidence/fixture/seed-verification.json
docs/dat/evidence/http-smoke.json
docs/dat/evidence/id-fix/legacy-inventory-verified.json
docs/dat/evidence/review/20261022204608/api-redis-evidence.json
docs/dat/evidence/review/20261022204608/environment.json
members/DAT.md
```

Rà scope/whitespace/secret-pattern/fingerprint không phải test chức năng mới. Không chạy lại test vì mã và phụ thuộc không đổi. Các bằng chứng chức năng vẫn là hai regression thật và23 ca P/R đã qua;2 review skip trong run chung đã chạy riêng. Backend/fixture đạt không gỡ blocker UI,manifest Sơn,tổng duyệt hoặc migration legacy.