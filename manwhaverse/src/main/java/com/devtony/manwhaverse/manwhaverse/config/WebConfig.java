package com.devtony.manwhaverse.manwhaverse.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
    registry.addMapping("/**")
            // The asterisk means "Allow any frontend URL to talk to me"
            .allowedOriginPatterns("*") 
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS");
}

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // Serve files from the 'downloads' directory at the root of the project
        // Access via http://localhost:8081/downloads/...
        registry.addResourceHandler("/downloads/**")
                .addResourceLocations("file:downloads/");
    }
}

