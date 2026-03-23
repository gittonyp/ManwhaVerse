package com.devtony.manwhaverse.manwhaverse.controller;

import com.devtony.manwhaverse.manwhaverse.model.Manwha;
import com.devtony.manwhaverse.manwhaverse.service.BookmarkService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/bookmarks")
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:5174"})
public class BookmarkController {
    
    @Autowired
    private BookmarkService bookmarkService;
    
    @GetMapping
    public ResponseEntity<List<Manwha>> getUserBookmarks(@RequestParam Long userId) {
        List<Manwha> bookmarks = bookmarkService.getUserBookmarks(userId);
        return ResponseEntity.ok(bookmarks);
    }
    
    @PostMapping("/toggle")
    public ResponseEntity<?> toggleBookmark(@RequestBody BookmarkRequest request) {
        boolean isBookmarked = bookmarkService.toggleBookmark(request.getUserId(), request.getMangaUrl());
        
        Map<String, Object> response = new HashMap<>();
        response.put("bookmarked", isBookmarked);
        response.put("message", isBookmarked ? "Added to bookmarks" : "Removed from bookmarks");
        
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/check")
    public ResponseEntity<?> checkBookmark(@RequestParam Long userId, @RequestParam String mangaUrl) {
        boolean isBookmarked = bookmarkService.isBookmarked(userId, mangaUrl);
        Map<String, Boolean> response = new HashMap<>();
        response.put("bookmarked", isBookmarked);
        return ResponseEntity.ok(response);
    }
    
    public static class BookmarkRequest {
        private Long userId;
        private String mangaUrl;
        
        public Long getUserId() { return userId; }
        public void setUserId(Long userId) { this.userId = userId; }
        public String getMangaUrl() { return mangaUrl; }
        public void setMangaUrl(String mangaUrl) { this.mangaUrl = mangaUrl; }
    }
}
