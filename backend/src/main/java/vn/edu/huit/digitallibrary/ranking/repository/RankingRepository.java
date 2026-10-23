package vn.edu.huit.digitallibrary.ranking.repository;

import java.util.List;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;
import vn.edu.huit.digitallibrary.ranking.dto.RankingEntry;

@Repository
public class RankingRepository {
    private static final String KEY = "ranking:books";
    private final StringRedisTemplate redis;

    public RankingRepository(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public RankingEntry increment(String bookId) {
        // ZINCRBY returns the new score; never read then increment in Java.
        Double score = redis.opsForZSet().incrementScore(KEY, bookId, 1);
        if (score == null) {
            throw new IllegalStateException("ZINCRBY did not return a score");
        }
        return new RankingEntry(bookId, score);
    }

    public List<RankingEntry> top(int count) {
        var entries = redis.opsForZSet().reverseRangeWithScores(KEY, 0, count - 1L);
        if (entries == null) {
            return List.of();
        }
        return entries.stream().map(entry -> new RankingEntry(entry.getValue(), entry.getScore())).toList();
    }
}
