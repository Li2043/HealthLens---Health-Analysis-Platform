package com.healthlens.platform.analysis;

import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/analysis")
public class AnalysisController {

    private final AnalysisService analysisService;

    public AnalysisController(AnalysisService analysisService) {
        this.analysisService = analysisService;
    }

    @PostMapping
    public ResponseEntity<AnalysisDetailResponse> analyse(@Valid @RequestBody AnalysisRequest request) {
        return ResponseEntity.ok(analysisService.analyse(request));
    }

    @GetMapping
    public ResponseEntity<List<AnalysisSummaryResponse>> listAnalyses() {
        return ResponseEntity.ok(analysisService.listForCurrentUser());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AnalysisDetailResponse> getAnalysis(@PathVariable UUID id) {
        return ResponseEntity.ok(analysisService.getForCurrentUser(id));
    }

    @DeleteMapping
    public ResponseEntity<Void> clearAnalyses() {
        analysisService.clearForCurrentUser();
        return ResponseEntity.noContent().build();
    }
}
