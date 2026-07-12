package com.healthlens.platform.security;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JwtSecretValidatorTest {

    @Test
    void acceptsStrongSecret() {
        List<String> issues = JwtSecretValidator.validate(
                "k8Jm2pQx9vL4nR7wY1zA6bC3dE0fG5hI8jK2lM4nP6qS9tU1vW3xY5zA7bC9dE"
        );
        assertTrue(issues.isEmpty());
    }

    @Test
    void rejectsPlaceholderSecret() {
        List<String> issues = JwtSecretValidator.validate(
                "change-me-use-a-long-random-secret-in-production"
        );
        assertFalse(issues.isEmpty());
    }

    @Test
    void rejectsShortSecret() {
        List<String> issues = JwtSecretValidator.validate("too-short");
        assertFalse(issues.isEmpty());
    }
}
