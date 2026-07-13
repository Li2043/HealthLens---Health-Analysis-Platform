package com.healthlens.platform.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "healthlens.demo-account")
public record DemoAccountProperties(
        boolean enabled,
        String email,
        String password,
        int dailyLimit
) {
    public DemoAccountProperties {
        if (dailyLimit <= 0) {
            dailyLimit = 20;
        }
    }

    public boolean isConfigured() {
        return email != null && !email.isBlank() && password != null && !password.isBlank();
    }

    public boolean matchesEmail(String candidateEmail) {
        return candidateEmail != null && email != null && email.equalsIgnoreCase(candidateEmail.trim());
    }
}
