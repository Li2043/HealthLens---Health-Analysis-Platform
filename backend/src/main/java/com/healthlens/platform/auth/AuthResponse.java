package com.healthlens.platform.auth;

import java.util.UUID;

public record AuthResponse(
        String token,
        String email,
        UUID userId
) {
}
