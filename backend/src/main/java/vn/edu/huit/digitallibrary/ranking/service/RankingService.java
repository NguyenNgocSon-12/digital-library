package vn.edu.huit.digitallibrary.ranking.service;

import java.util.List;
import org.bson.types.ObjectId;
import org.springframework.stereotype.Service;
import vn.edu.huit.digitallibrary.catalog.service.BookService;
import vn.edu.huit.digitallibrary.common.ApiException;
import vn.edu.huit.digitallibrary.ranking.dto.RankingEntry;
import vn.edu.huit.digitallibrary.ranking.repository.RankingRepository;

@Service
public class RankingService {
    private final RankingRepository ranking;
    private final BookService books;

    public RankingService(RankingRepository ranking, BookService books) {
        this.ranking = ranking;
        this.books = books;
    }

    public RankingEntry recordRead(String bookId) {
        bookId = canonicalId(bookId);
        if (!books.exists(bookId)) {
            throw ApiException.notFound("Không tìm thấy sách " + bookId);
        }
        return ranking.increment(bookId);
    }

    public List<RankingEntry> top(int count) {
        if (count < 1 || count > 100) {
            throw ApiException.badRequest("top phải trong khoảng 1..100");
        }
        // Normalize the read DTO too, without modifying or silently merging legacy Redis members.
        return ranking.top(count).stream()
                .map(entry -> new RankingEntry(canonicalId(entry.bookId()), entry.score())).toList();
    }

    private static String canonicalId(String id) {
        return ObjectId.isValid(id) ? new ObjectId(id).toHexString() : id;
    }
}
