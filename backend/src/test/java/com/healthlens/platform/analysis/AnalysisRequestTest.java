package com.healthlens.platform.analysis;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class AnalysisRequestTest {

    @Test
    void defaultsModeToDeepSeekWhenOmitted() {
        AnalysisRequest request = new AnalysisRequest("heart rate 100", "en", null);

        assertEquals("deepseek", request.mode());
    }

    @Test
    void defaultsModeToDeepSeekWhenBlank() {
        AnalysisRequest request = new AnalysisRequest("heart rate 100", "en", "   ");

        assertEquals("deepseek", request.mode());
    }

    @Test
    void preservesExplicitMode() {
        AnalysisRequest request = new AnalysisRequest("heart rate 100", "en", "mock");

        assertEquals("mock", request.mode());
    }
}
