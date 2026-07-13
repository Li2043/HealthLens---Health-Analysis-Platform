package com.healthlens.platform.analysis;

public record AnalysisQuotaResponse(
        int dailyLimit,
        long usedToday,
        long remainingToday
) {
}
