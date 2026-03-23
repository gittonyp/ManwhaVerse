package com.devtony.manwhaverse.manwhaverse.controller;

import com.devtony.manwhaverse.manwhaverse.entity.Comment;
import com.devtony.manwhaverse.manwhaverse.service.CommentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/comments")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:5174"})
public class CommentController {
    
    @Autowired
    private CommentService commentService;
    
    @GetMapping("/{mangaId}")
    public ResponseEntity<List<CommentResponse>> getComments(@PathVariable String mangaId) {
        // NOTE: PathVariable might need decoding if it contains slashes, but Spring usually handles it if encoded.
        // If "manga/solo-leveling" is passed, it might be tricky.
        // Actually, normally we pass ID as query param if it's complex, or we need to ensure it's URL encoded double.
        // Let's use request param for safety like in Bookmarks.
        return null; 
    }
    
    @GetMapping
    public ResponseEntity<List<CommentResponse>> getCommentsByParam(
            @RequestParam String mangaUrl,
            @RequestParam(required = false) Long chapterId
    ) {
         List<Comment> comments = commentService.getComments(mangaUrl, chapterId);
         List<CommentResponse> response = comments.stream()
                 .map(c -> new CommentResponse(
                         c.getId(),
                         c.getUser().getUsername(),
                         c.getContent(),
                         c.getCreatedAt()
                 ))
                 .collect(Collectors.toList());
         return ResponseEntity.ok(response);
    }
    
    @PostMapping
    public ResponseEntity<CommentResponse> addComment(@RequestBody CommentRequest request) {
        Comment comment = commentService.addComment(
                request.getUserId(), 
                request.getMangaUrl(), 
                request.getContent(),
                request.getChapterId()
        );
        CommentResponse response = new CommentResponse(
                comment.getId(),
                comment.getUser().getUsername(),
                comment.getContent(),
                comment.getCreatedAt()
        );
        return ResponseEntity.ok(response);
    }
    
    // DTOs
    public static class CommentRequest {
        private Long userId;
        private String mangaUrl;
        private String content;
        private Long chapterId; // Optional
        
        // Getters/Setters
        public Long getUserId() { return userId; }
        public void setUserId(Long userId) { this.userId = userId; }
        public String getMangaUrl() { return mangaUrl; }
        public void setMangaUrl(String mangaUrl) { this.mangaUrl = mangaUrl; }
        public String getContent() { return content; }
        public void setContent(String content) { this.content = content; }
        public Long getChapterId() { return chapterId; }
        public void setChapterId(Long chapterId) { this.chapterId = chapterId; }
    }
    
    public static class CommentResponse {
        private Long id;
        private String username;
        private String content;
        private String createdAt;
        
        public CommentResponse(Long id, String username, String content, String createdAt) {
            this.id = id;
            this.username = username;
            this.content = content;
            this.createdAt = createdAt;
        }
        
        // Getters
        public Long getId() { return id; }
        public String getUsername() { return username; }
        public String getContent() { return content; }
        public String getCreatedAt() { return createdAt; }
    }
}
