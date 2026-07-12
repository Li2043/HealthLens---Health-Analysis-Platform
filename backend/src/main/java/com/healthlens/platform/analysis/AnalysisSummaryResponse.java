package com.healthlens.platform.analysis;

import java.time.Instant;
import java.util.UUID;

public record AnalysisSummaryResponse(
        UUID id,
        String inputText,
        String language,
        String riskLevel,
        String triageTier,
        Instant createdAt
) {
}
