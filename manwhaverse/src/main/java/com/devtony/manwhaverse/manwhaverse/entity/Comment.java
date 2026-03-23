package com.devtony.manwhaverse.manwhaverse.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "comments")
public class Comment {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "manga_url", nullable = false)
    private String mangaUrl;
    
    @Column(name = "content", nullable = false, length = 1000)
    private String content;
    
    @Column(name = "created_at")
    private String createdAt;
    
    @Column(name = "chapter_id")
    private Long chapterId;
    
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    // Constructors
    public Comment() {
        this.createdAt = java.time.LocalDateTime.now().toString();
    }
    
    public Comment(User user, String mangaUrl, String content, Long chapterId) {
        this.user = user;
        this.mangaUrl = mangaUrl;
        this.content = content;
        this.chapterId = chapterId;
        this.createdAt = java.time.LocalDateTime.now().toString();
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public Long getChapterId() { return chapterId; }
    public void setChapterId(Long chapterId) { this.chapterId = chapterId; }
    
    public String getMangaUrl() { return mangaUrl; }
    public void setMangaUrl(String mangaUrl) { this.mangaUrl = mangaUrl; }
    
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
}
