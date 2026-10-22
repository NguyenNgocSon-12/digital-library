package vn.edu.huit.digitallibrary.reading.service;

import java.time.Instant;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;
import vn.edu.huit.digitallibrary.catalog.service.BookService;
import vn.edu.huit.digitallibrary.common.ApiException;
import vn.edu.huit.digitallibrary.identity.auth.CurrentUser;
import vn.edu.huit.digitallibrary.identity.service.UserService;
import vn.edu.huit.digitallibrary.reading.dto.ProgressRequest;
import vn.edu.huit.digitallibrary.reading.dto.ProgressResponse;
import vn.edu.huit.digitallibrary.reading.repository.ProgressRepository;

@Service
public class ProgressService {
    private final ProgressRepository progress;
    private final BookService books;
    private final UserService users;

    public ProgressService(ProgressRepository progress, BookService books, UserService users) {
        this.progress = progress;
        this.books = books;
        this.users = users;
    }

    public ProgressResponse save(String userId, String bookId, ProgressRequest request, CurrentUser currentUser) {
        userId = canonicalId(userId);
        bookId = canonicalId(bookId);
        requireAccess(userId, bookId, currentUser);
        // Use the public catalog service, never catalog repositories/documents.
        books.getChapter(bookId, request.chapter());
        ProgressResponse result = new ProgressResponse(request.chapter(), request.page(), request.line(), Instant.now());
        progress.save(userId, bookId, result);
        return result;
    }

    public ProgressResponse get(String userId, String bookId, CurrentUser currentUser) {
        userId = canonicalId(userId);
        bookId = canonicalId(bookId);
        requireAccess(userId, bookId, currentUser);
        return progress.find(userId, bookId)
                .orElseThrow(() -> ApiException.notFound("Chưa có tiến trình đọc"));
    }

    private void requireAccess(String userId, String bookId, CurrentUser currentUser) {
        if (!currentUser.canAccess(userId)) {
            throw ApiException.forbidden("Không có quyền truy cập tiến trình đọc");
        }
        // Auth already verifies the current user; admin targets need a separate lookup.
        if (!currentUser.id().equals(userId)) {
            users.get(userId);
        }
        if (!books.exists(bookId)) {
            throw ApiException.notFound("Không tìm thấy sách " + bookId);
        }
    }

    private static String canonicalId(String id) {
        // Leave invalid IDs untouched so authorization and existing 404 handling keep their order.
        return ObjectId.isValid(id) ? new ObjectId(id).toHexString() : id;
    }
}
