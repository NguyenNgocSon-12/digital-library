package vn.edu.huit.digitallibrary.reading.dto;

import java.time.Instant;

public record ProgressResponse(int chapter, int page, int line, Instant updatedAt) {}
