package com.healthlens.platform.user;

import com.healthlens.platform.config.DemoAccountProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DemoAccountInitializer implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(DemoAccountInitializer.class);

    private final DemoAccountProperties demoAccountProperties;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public DemoAccountInitializer(
            DemoAccountProperties demoAccountProperties,
            UserRepository userRepository,
            PasswordEncoder passwordEncoder
    ) {
        this.demoAccountProperties = demoAccountProperties;
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (!demoAccountProperties.enabled() || !demoAccountProperties.isConfigured()) {
            return;
        }

        String email = demoAccountProperties.email().trim();
        userRepository.findByEmailIgnoreCase(email).ifPresentOrElse(
                user -> log.info("Demo account already exists: {}", email),
                () -> {
                    User user = new User(email, passwordEncoder.encode(demoAccountProperties.password()));
                    userRepository.save(user);
                    log.info(
                            "Created demo account {} with daily analysis limit {}",
                            email,
                            demoAccountProperties.dailyLimit()
                    );
                }
        );
    }
}
