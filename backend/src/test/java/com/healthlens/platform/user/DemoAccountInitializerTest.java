package com.healthlens.platform.user;

import com.healthlens.platform.config.DemoAccountProperties;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class DemoAccountInitializerTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @Test
    void createsDemoAccountWhenMissing() {
        DemoAccountProperties properties = new DemoAccountProperties(
                true,
                "demo@healthlens.demo",
                "demo1234",
                20
        );
        when(userRepository.findByEmailIgnoreCase("demo@healthlens.demo")).thenReturn(Optional.empty());
        when(passwordEncoder.encode("demo1234")).thenReturn("encoded-password");

        DemoAccountInitializer initializer = new DemoAccountInitializer(
                properties,
                userRepository,
                passwordEncoder
        );
        initializer.run(null);

        ArgumentCaptor<User> userCaptor = ArgumentCaptor.forClass(User.class);
        verify(userRepository).save(userCaptor.capture());
        assertEquals("demo@healthlens.demo", userCaptor.getValue().getEmail());
        assertEquals("encoded-password", userCaptor.getValue().getPasswordHash());
    }

    @Test
    void skipsCreationWhenDemoAccountAlreadyExists() {
        DemoAccountProperties properties = new DemoAccountProperties(
                true,
                "demo@healthlens.demo",
                "demo1234",
                20
        );
        when(userRepository.findByEmailIgnoreCase("demo@healthlens.demo"))
                .thenReturn(Optional.of(new User("demo@healthlens.demo", "existing")));

        DemoAccountInitializer initializer = new DemoAccountInitializer(
                properties,
                userRepository,
                passwordEncoder
        );
        initializer.run(null);

        verify(userRepository, never()).save(any());
    }

    @Test
    void skipsCreationWhenDisabled() {
        DemoAccountProperties properties = new DemoAccountProperties(
                false,
                "demo@healthlens.demo",
                "demo1234",
                20
        );

        DemoAccountInitializer initializer = new DemoAccountInitializer(
                properties,
                userRepository,
                passwordEncoder
        );
        initializer.run(null);

        verify(userRepository, never()).findByEmailIgnoreCase(any());
    }
}
