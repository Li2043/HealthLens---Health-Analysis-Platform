package com.healthlens.platform.analysis;

import com.fasterxml.jackson.databind.JsonNode;

import java.time.Instant;
import java.util.UUID;

public record AnalysisDetailResponse(
        UUID id,
        String inputText,
        String language,
        String riskLevel,
        String triageTier,
        Instant createdAt,
        JsonNode result
) {
}
