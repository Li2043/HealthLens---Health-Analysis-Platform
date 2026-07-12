package com.healthlens.platform.analysis;

import com.fasterxml.jackson.databind.JsonNode;
import com.healthlens.platform.auth.AuthenticatedUserService;
import com.healthlens.platform.client.AiServiceClient;
import com.healthlens.platform.user.User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class AnalysisService {

    private final AiServiceClient aiServiceClient;
    private final AnalysisRecordRepository analysisRecordRepository;
    private final AuthenticatedUserService authenticatedUserService;

    public AnalysisService(
            AiServiceClient aiServiceClient,
            AnalysisRecordRepository analysisRecordRepository,
            AuthenticatedUserService authenticatedUserService
    ) {
        this.aiServiceClient = aiServiceClient;
        this.analysisRecordRepository = analysisRecordRepository;
        this.authenticatedUserService = authenticatedUserService;
    }

    @Transactional
    public AnalysisDetailResponse analyse(AnalysisRequest request) {
        User user = authenticatedUserService.requireCurrentUser();
        JsonNode result = aiServiceClient.analyse(request);

        AnalysisRecord record = new AnalysisRecord(
                user,
                request.text().trim(),
                request.language(),
                extractRiskLevel(result),
                extractTriageTier(result),
                result
        );

        AnalysisRecord saved = analysisRecordRepository.save(record);
        return toDetailResponse(saved);
    }

    @Transactional(readOnly = true)
    public List<AnalysisSummaryResponse> listForCurrentUser() {
        User user = authenticatedUserService.requireCurrentUser();
        return analysisRecordRepository.findByUser_IdOrderByCreatedAtDesc(user.getId()).stream()
                .map(this::toSummaryResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public AnalysisDetailResponse getForCurrentUser(UUID id) {
        User user = authenticatedUserService.requireCurrentUser();
        AnalysisRecord record = analysisRecordRepository.findByIdAndUserId(id, user.getId())
                .orElseThrow(() -> new AnalysisNotFoundException(id));
        return toDetailResponse(record);
    }

    @Transactional
    public void clearForCurrentUser() {
        User user = authenticatedUserService.requireCurrentUser();
        analysisRecordRepository.deleteByUser_Id(user.getId());
    }

    private String extractRiskLevel(JsonNode result) {
        return result.path("risk_result").path("risk_level").asText("unknown");
    }

    private String extractTriageTier(JsonNode result) {
        return result.path("escalation").path("triage_tier").asText("unknown");
    }

    private AnalysisSummaryResponse toSummaryResponse(AnalysisRecord record) {
        return new AnalysisSummaryResponse(
                record.getId(),
                record.getInputText(),
                record.getLanguage(),
                record.getRiskLevel(),
                record.getTriageTier(),
                record.getCreatedAt()
        );
    }

    private AnalysisDetailResponse toDetailResponse(AnalysisRecord record) {
        return new AnalysisDetailResponse(
                record.getId(),
                record.getInputText(),
                record.getLanguage(),
                record.getRiskLevel(),
                record.getTriageTier(),
                record.getCreatedAt(),
                record.getResultJson()
        );
    }
}
