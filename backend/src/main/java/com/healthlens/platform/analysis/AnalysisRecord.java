package com.healthlens.platform.analysis;

import com.fasterxml.jackson.databind.JsonNode;
import com.healthlens.platform.user.User;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "analyses")
public class AnalysisRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(name = "input_text", nullable = false, columnDefinition = "TEXT")
    private String inputText;

    @Column(nullable = false, length = 2)
    private String language;

    @Column(name = "risk_level", nullable = false, length = 20)
    private String riskLevel;

    @Column(name = "triage_tier", nullable = false, length = 20)
    private String triageTier;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "result_json", nullable = false, columnDefinition = "jsonb")
    private JsonNode resultJson;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    protected AnalysisRecord() {
    }

    public AnalysisRecord(
            User user,
            String inputText,
            String language,
            String riskLevel,
            String triageTier,
            JsonNode resultJson
    ) {
        this.user = user;
        this.inputText = inputText;
        this.language = language;
        this.riskLevel = riskLevel;
        this.triageTier = triageTier;
        this.resultJson = resultJson;
        this.createdAt = Instant.now();
    }

    public UUID getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public String getInputText() {
        return inputText;
    }

    public String getLanguage() {
        return language;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public String getTriageTier() {
        return triageTier;
    }

    public JsonNode getResultJson() {
        return resultJson;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
