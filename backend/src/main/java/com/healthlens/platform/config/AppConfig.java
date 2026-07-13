package com.healthlens.platform.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties({
        AiServiceProperties.class,
        JwtProperties.class,
        AnalysisQuotaProperties.class,
        DemoAccountProperties.class
})
public class AppConfig {
}
