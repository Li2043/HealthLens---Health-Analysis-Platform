package com.healthlens.platform.analysis;

import com.healthlens.platform.config.AnalysisQuotaProperties;
import com.healthlens.platform.config.DemoAccountProperties;
import com.healthlens.platform.user.User;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;

@Service
public class AnalysisQuotaService {

    private final AnalysisRecordRepository analysisRecordRepository;
    private final AnalysisQuotaProperties analysisQuotaProperties;
    private final DemoAccountProperties demoAccountProperties;

    public AnalysisQuotaService(
            AnalysisRecordRepository analysisRecordRepository,
            AnalysisQuotaProperties analysisQuotaProperties,
            DemoAccountProperties demoAccountProperties
    ) {
        this.analysisRecordRepository = analysisRecordRepository;
        this.analysisQuotaProperties = analysisQuotaProperties;
        this.demoAccountProperties = demoAccountProperties;
    }

    public void enforceDailyLimit(User user, String language) {
        AnalysisQuotaResponse status = getQuotaStatus(user);
        if (status.usedToday() >= status.dailyLimit()) {
            throw new DailyAnalysisLimitExceededException(language, status.dailyLimit());
        }
    }

    public AnalysisQuotaResponse getQuotaStatus(User user) {
        int dailyLimit = dailyLimitFor(user);
        Instant dayStart = startOfUtcDay();
        Instant dayEnd = dayStart.plusSeconds(86_400);

        long usedToday = analysisRecordRepository
                .countByUser_IdAndCreatedAtGreaterThanEqualAndCreatedAtLessThan(
                        user.getId(),
                        dayStart,
                        dayEnd
                );

        long remainingToday = Math.max(0, dailyLimit - usedToday);
        return new AnalysisQuotaResponse(dailyLimit, usedToday, remainingToday);
    }

    int dailyLimitFor(User user) {
        if (demoAccountProperties.enabled() && demoAccountProperties.matchesEmail(user.getEmail())) {
            return demoAccountProperties.dailyLimit();
        }
        return analysisQuotaProperties.dailyLimit();
    }

    static Instant startOfUtcDay() {
        return LocalDate.now(ZoneOffset.UTC)
                .atStartOfDay()
                .toInstant(ZoneOffset.UTC);
    }
}
