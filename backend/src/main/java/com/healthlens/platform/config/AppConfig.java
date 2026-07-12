package com.healthlens.platform.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties({AiServiceProperties.class, JwtProperties.class})
public class AppConfig {
}
