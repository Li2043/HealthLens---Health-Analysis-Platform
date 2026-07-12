package com.healthlens.platform.security;

import com.healthlens.platform.config.JwtProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.env.Environment;
import org.springframework.core.env.Profiles;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;

@Component
public class JwtSecretValidator implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(JwtSecretValidator.class);

    private static final int MIN_SECRET_LENGTH = 32;

    private static final Set<String> FORBIDDEN_SECRETS = Set.of(
            "change-me-use-a-long-random-secret-in-production",
            "changeme",
            "secret",
            "jwt-secret",
            "your-secret-key",
            "password",
            "test-secret-must-be-at-least-32-characters-long"
    );

    private final JwtProperties jwtProperties;
    private final Environment environment;

    public JwtSecretValidator(JwtProperties jwtProperties, Environment environment) {
        this.jwtProperties = jwtProperties;
        this.environment = environment;
    }

    @Override
    public void run(ApplicationArguments args) {
        List<String> issues = validate(jwtProperties.secret());
        if (issues.isEmpty()) {
            return;
        }

        String message = "JWT_SECRET is not safe: " + String.join(", ", issues)
                + ". Generate one with scripts/generate-jwt-secret.ps1 or scripts/generate-jwt-secret.sh";

        if (isProductionEnvironment()) {
            throw new IllegalStateException(message);
        }

        log.warn("Development mode: {}", message);
    }

    static List<String> validate(String secret) {
        List<String> issues = new ArrayList<>();
        if (secret == null || secret.isBlank()) {
            issues.add("missing");
            return issues;
        }

        String normalized = secret.trim().toLowerCase(Locale.ROOT);
        if (secret.trim().length() < MIN_SECRET_LENGTH) {
            issues.add("must be at least " + MIN_SECRET_LENGTH + " characters");
        }
        if (FORBIDDEN_SECRETS.contains(normalized)) {
            issues.add("uses a known weak default value");
        }
        if (normalized.contains("change-me") || normalized.contains("changeme")) {
            issues.add("looks like a placeholder");
        }
        return issues;
    }

    private boolean isProductionEnvironment() {
        return environment.acceptsProfiles(Profiles.of("prod", "production"));
    }
}
