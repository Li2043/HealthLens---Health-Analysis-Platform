package com.healthlens.platform.analysis;

import com.healthlens.platform.config.AnalysisQuotaProperties;
import com.healthlens.platform.config.DemoAccountProperties;
import com.healthlens.platform.user.User;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.lang.reflect.Field;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AnalysisQuotaServiceTest {

    private static final DemoAccountProperties DISABLED_DEMO = new DemoAccountProperties(
            false,
            "demo@healthlens.demo",
            "demo1234",
            20
    );

    private static final DemoAccountProperties ENABLED_DEMO = new DemoAccountProperties(
            true,
            "demo@healthlens.demo",
            "demo1234",
            20
    );

    @Mock
    private AnalysisRecordRepository analysisRecordRepository;

    @Test
    void allowsAnalysisWhenBelowDailyLimit() {
        when(analysisRecordRepository.countByUser_IdAndCreatedAtGreaterThanEqualAndCreatedAtLessThan(
                any(UUID.class),
                any(),
                any()
        )).thenReturn(9L);

        AnalysisQuotaService service = new AnalysisQuotaService(
                analysisRecordRepository,
                new AnalysisQuotaProperties(10),
                DISABLED_DEMO
        );

        assertDoesNotThrow(() -> service.enforceDailyLimit(user("user@example.com"), "en"));
    }

    @Test
    void rejectsAnalysisWhenDailyLimitReachedEnglish() {
        User user = user("user@example.com");
        when(analysisRecordRepository.countByUser_IdAndCreatedAtGreaterThanEqualAndCreatedAtLessThan(
                eq(user.getId()),
                any(),
                any()
        )).thenReturn(10L);

        AnalysisQuotaService service = new AnalysisQuotaService(
                analysisRecordRepository,
                new AnalysisQuotaProperties(10),
                DISABLED_DEMO
        );

        DailyAnalysisLimitExceededException ex = assertThrows(
                DailyAnalysisLimitExceededException.class,
                () -> service.enforceDailyLimit(user, "en")
        );

        assertEquals(
                "Daily analysis limit reached (10 per day). Try again tomorrow.",
                ex.getMessage()
        );
    }

    @Test
    void rejectsAnalysisWhenDailyLimitReachedChinese() {
        when(analysisRecordRepository.countByUser_IdAndCreatedAtGreaterThanEqualAndCreatedAtLessThan(
                any(UUID.class),
                any(),
                any()
        )).thenReturn(10L);

        AnalysisQuotaService service = new AnalysisQuotaService(
                analysisRecordRepository,
                new AnalysisQuotaProperties(10),
                DISABLED_DEMO
        );

        DailyAnalysisLimitExceededException ex = assertThrows(
                DailyAnalysisLimitExceededException.class,
                () -> service.enforceDailyLimit(user("user@example.com"), "zh")
        );

        assertEquals("今日分析次数已达上限（每日 10 次），请明天再试。", ex.getMessage());
    }

    @Test
    void returnsQuotaStatus() {
        when(analysisRecordRepository.countByUser_IdAndCreatedAtGreaterThanEqualAndCreatedAtLessThan(
                any(UUID.class),
                any(),
                any()
        )).thenReturn(4L);

        AnalysisQuotaService service = new AnalysisQuotaService(
                analysisRecordRepository,
                new AnalysisQuotaProperties(10),
                DISABLED_DEMO
        );

        AnalysisQuotaResponse status = service.getQuotaStatus(user("user@example.com"));
        assertEquals(10, status.dailyLimit());
        assertEquals(4, status.usedToday());
        assertEquals(6, status.remainingToday());
    }

    @Test
    void demoAccountUsesHigherDailyLimit() {
        when(analysisRecordRepository.countByUser_IdAndCreatedAtGreaterThanEqualAndCreatedAtLessThan(
                any(UUID.class),
                any(),
                any()
        )).thenReturn(15L);

        AnalysisQuotaService service = new AnalysisQuotaService(
                analysisRecordRepository,
                new AnalysisQuotaProperties(10),
                ENABLED_DEMO
        );

        AnalysisQuotaResponse status = service.getQuotaStatus(user("demo@healthlens.demo"));
        assertEquals(20, status.dailyLimit());
        assertEquals(15, status.usedToday());
        assertEquals(5, status.remainingToday());
        assertDoesNotThrow(() -> service.enforceDailyLimit(user("demo@healthlens.demo"), "en"));
    }

    @Test
    void demoAccountRejectsWhenDemoLimitReached() {
        when(analysisRecordRepository.countByUser_IdAndCreatedAtGreaterThanEqualAndCreatedAtLessThan(
                any(UUID.class),
                any(),
                any()
        )).thenReturn(20L);

        AnalysisQuotaService service = new AnalysisQuotaService(
                analysisRecordRepository,
                new AnalysisQuotaProperties(10),
                ENABLED_DEMO
        );

        DailyAnalysisLimitExceededException ex = assertThrows(
                DailyAnalysisLimitExceededException.class,
                () -> service.enforceDailyLimit(user("demo@healthlens.demo"), "en")
        );

        assertEquals(
                "Daily analysis limit reached (20 per day). Try again tomorrow.",
                ex.getMessage()
        );
    }

    private static User user(String email) {
        User user = new User(email, "hashed-password");
        try {
            Field idField = User.class.getDeclaredField("id");
            idField.setAccessible(true);
            idField.set(user, UUID.randomUUID());
        } catch (ReflectiveOperationException ex) {
            throw new IllegalStateException("Failed to assign test user id", ex);
        }
        return user;
    }
}
