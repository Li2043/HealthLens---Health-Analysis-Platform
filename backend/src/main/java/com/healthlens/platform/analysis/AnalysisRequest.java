package com.healthlens.platform.analysis;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public record AnalysisRequest(
        @NotBlank(message = "text is required")
        String text,

        @Pattern(regexp = "en|zh", message = "language must be en or zh")
        String language,

        @Pattern(regexp = "mock|ai|openai|deepseek", message = "mode must be mock, ai, openai, or deepseek")
        String mode
) {
    public AnalysisRequest {
        if (language == null || language.isBlank()) {
            language = "en";
        }
        if (mode == null || mode.isBlank()) {
            mode = "mock";
        }
    }
}
