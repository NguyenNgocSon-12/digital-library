package vn.edu.huit.digitallibrary.reading.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import tools.jackson.databind.annotation.JsonDeserialize;

public record ProgressRequest(
        @NotNull @Min(1) @JsonDeserialize(using = ProgressIntegerDeserializer.class) Integer chapter,
        @NotNull @Min(1) @JsonDeserialize(using = ProgressIntegerDeserializer.class) Integer page,
        @NotNull @Min(0) @JsonDeserialize(using = ProgressIntegerDeserializer.class) Integer line) {}
