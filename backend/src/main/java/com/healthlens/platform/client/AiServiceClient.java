package com.healthlens.platform.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.healthlens.platform.analysis.AnalysisRequest;
import com.healthlens.platform.config.AiServiceProperties;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

/**
 * HTTP client for the internal FastAPI AI service.
 */
@Component
public class AiServiceClient {

    private final RestClient restClient;

    public AiServiceClient(RestClient.Builder restClientBuilder, AiServiceProperties properties) {
        this.restClient = restClientBuilder
                .baseUrl(properties.baseUrl())
                .build();
    }

    public String fetchHealthStatus() {
        return restClient.get()
                .uri("/health")
                .retrieve()
                .body(String.class);
    }

    public JsonNode analyse(AnalysisRequest request) {
        return restClient.post()
                .uri("/analyse")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(JsonNode.class);
    }
}
