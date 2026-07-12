package com.healthlens.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "healthlens.ai-service")
public record AiServiceProperties(String baseUrl) {
}
