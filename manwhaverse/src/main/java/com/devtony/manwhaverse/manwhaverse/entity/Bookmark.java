package com.devtony.manwhaverse.manwhaverse.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "bookmarks")
public class Bookmark {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "user_id", nullable = false)
    private Long userId;
    
    @Column(name = "manga_url", nullable = false)
    private String mangaUrl;
    
    @Column(name = "created_at")
    private String createdAt;
    
    // Constructors
    public Bookmark() {
        this.createdAt = java.time.LocalDateTime.now().toString();
    }
    
    public Bookmark(Long userId, String mangaUrl) {
        this.userId = userId;
        this.mangaUrl = mangaUrl;
        this.createdAt = java.time.LocalDateTime.now().toString();
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    
    public String getMangaUrl() { return mangaUrl; }
    public void setMangaUrl(String mangaUrl) { this.mangaUrl = mangaUrl; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
