package com.healthlens.platform.analysis;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.healthlens.platform.common.GlobalExceptionHandler;
import com.healthlens.platform.security.JwtAuthenticationEntryPoint;
import com.healthlens.platform.security.JwtAuthenticationFilter;
import com.healthlens.platform.security.JwtService;
import com.healthlens.platform.security.SecurityConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(AnalysisController.class)
@Import({
        SecurityConfig.class,
        GlobalExceptionHandler.class,
        JwtAuthenticationFilter.class,
        JwtAuthenticationEntryPoint.class
})
class AnalysisControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private AnalysisService analysisService;

    @MockBean
    private JwtService jwtService;

    @Test
    void analyseRequiresAuthentication() throws Exception {
        mockMvc.perform(post("/api/analysis")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"text":"My heart rate is 100 and I cannot sleep","language":"en"}
                                """))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.message").value("Authentication required"));
    }

    @Test
    @WithMockUser(username = "user@example.com")
    void analyseReturnsSavedAnalysis() throws Exception {
        ObjectNode result = objectMapper.createObjectNode();
        result.putObject("risk_result").put("risk_level", "moderate");
        result.put("explanation", "Please monitor your symptoms.");

        UUID id = UUID.randomUUID();
        when(analysisService.analyse(any(AnalysisRequest.class)))
                .thenReturn(new AnalysisDetailResponse(
                        id,
                        "My heart rate is 100 and I cannot sleep",
                        "en",
                        "moderate",
                        "moderate",
                        Instant.parse("2026-07-12T10:00:00Z"),
                        result
                ));

        mockMvc.perform(post("/api/analysis")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"text":"My heart rate is 100 and I cannot sleep","language":"en"}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(id.toString()))
                .andExpect(jsonPath("$.riskLevel").value("moderate"))
                .andExpect(jsonPath("$.result.risk_result.risk_level").value("moderate"));
    }

    @Test
    @WithMockUser(username = "user@example.com")
    void analyseRejectsBlankText() throws Exception {
        when(analysisService.analyse(any(AnalysisRequest.class)))
                .thenThrow(new IllegalArgumentException("should not be called"));

        mockMvc.perform(post("/api/analysis")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"text":"   ","language":"en"}
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").value("text is required"));
    }
}
