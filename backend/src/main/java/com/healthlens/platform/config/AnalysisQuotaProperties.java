package com.healthlens.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "healthlens.analysis")
public record AnalysisQuotaProperties(
        int dailyLimit
) {
    public AnalysisQuotaProperties {
        if (dailyLimit <= 0) {
            dailyLimit = 10;
        }
    }
}
