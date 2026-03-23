package com.devtony.manwhaverse.manwhaverse.service;

import com.devtony.manwhaverse.manwhaverse.entity.User;
import com.devtony.manwhaverse.manwhaverse.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;
import java.util.UUID;

@Service
public class AuthService {
    
    @Autowired
    private UserRepository userRepository;
    
    private BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    
    public User register(String username, String email, String password) throws Exception {
        // Check if username exists
        if (userRepository.existsByUsername(username)) {
            throw new Exception("Username already exists");
        }
        
        // Check if email exists
        if (userRepository.existsByEmail(email)) {
            throw new Exception("Email already exists");
        }
        
        // Hash password
        String hashedPassword = passwordEncoder.encode(password);
        
        // Create user
        User user = new User(username, email, hashedPassword);
        
        return userRepository.save(user);
    }
    
    public AuthResult login(String username, String password) throws Exception {
        // Find user
        Optional<User> userOpt = userRepository.findByUsername(username);
        
        if (userOpt.isEmpty()) {
            throw new Exception("Invalid username or password");
        }
        
        User user = userOpt.get();
        
        // Verify password
        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new Exception("Invalid username or password");
        }
        
        // Generate simple token (in production, use JWT)
        String token = UUID.randomUUID().toString();
        
        return new AuthResult(token, user);
    }
    
    // Inner class for auth result
    public static class AuthResult {
        private String token;
        private User user;
        
        public AuthResult(String token, User user) {
            this.token = token;
            this.user = user;
        }
        
        public String getToken() {
            return token;
        }
        
        public User getUser() {
            return user;
        }
    }
}
