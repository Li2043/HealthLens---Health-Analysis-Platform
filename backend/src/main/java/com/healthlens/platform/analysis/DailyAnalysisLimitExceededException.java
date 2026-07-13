package com.healthlens.platform.analysis;

public class DailyAnalysisLimitExceededException extends RuntimeException {

    public DailyAnalysisLimitExceededException(String language, int dailyLimit) {
        super(messageFor(language, dailyLimit));
    }

    static String messageFor(String language, int dailyLimit) {
        if ("zh".equalsIgnoreCase(language)) {
            return "今日分析次数已达上限（每日 " + dailyLimit + " 次），请明天再试。";
        }
        return "Daily analysis limit reached (" + dailyLimit + " per day). Try again tomorrow.";
    }
}
