package vn.edu.huit.digitallibrary.reading.repository;

import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;
import vn.edu.huit.digitallibrary.reading.dto.ProgressResponse;

@Repository
public class ProgressRepository {
    private final StringRedisTemplate redis;

    public ProgressRepository(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public void save(String userId, String bookId, ProgressResponse progress) {
        // One HSET updates the complete position atomically; no TTL in the demo.
        redis.opsForHash().putAll(key(userId, bookId), Map.of(
                "chapter", Integer.toString(progress.chapter()),
                "page", Integer.toString(progress.page()),
                "line", Integer.toString(progress.line()),
                "updatedAt", progress.updatedAt().toString()));
    }

    public Optional<ProgressResponse> find(String userId, String bookId) {
        Map<Object, Object> fields = redis.opsForHash().entries(key(userId, bookId));
        if (fields.isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(new ProgressResponse(
                Integer.parseInt((String) fields.get("chapter")),
                Integer.parseInt((String) fields.get("page")),
                Integer.parseInt((String) fields.get("line")),
                Instant.parse((String) fields.get("updatedAt"))));
    }

    private String key(String userId, String bookId) {
        return "progress:" + userId + ":" + bookId;
    }
}
