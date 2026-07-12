package com.healthlens.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "healthlens.jwt")
public record JwtProperties(
        String secret,
        long expirationMs
) {
}
