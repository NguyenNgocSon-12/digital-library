package vn.edu.huit.digitallibrary.ranking.controller;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import vn.edu.huit.digitallibrary.ranking.dto.RankingEntry;
import vn.edu.huit.digitallibrary.ranking.service.RankingService;

@RestController
public class RankingController {
    private final RankingService ranking;

    public RankingController(RankingService ranking) {
        this.ranking = ranking;
    }

    @PostMapping("/api/books/{bookId}/read")
    public RankingEntry recordRead(@PathVariable String bookId) {
        return ranking.recordRead(bookId);
    }

    @GetMapping("/api/ranking")
    public List<RankingEntry> top(@RequestParam(defaultValue = "10") int top) {
        return ranking.top(top);
    }
}
