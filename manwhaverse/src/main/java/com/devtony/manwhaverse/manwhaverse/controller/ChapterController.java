package com.devtony.manwhaverse.manwhaverse.controller;

import com.devtony.manwhaverse.manwhaverse.model.Chapter;
import com.devtony.manwhaverse.manwhaverse.service.ChapterService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/chapters")
public class ChapterController {

    @Autowired
    private ChapterService chapterService;

    @GetMapping("/{id}")
    public ResponseEntity<ChapterDetailedResponse> getChapter(@PathVariable Long id) {
        return chapterService.getChapterDetails(id)
                .map(chapter -> {
                    ChapterDetailedResponse dto = new ChapterDetailedResponse();
                    dto.setId(chapter.getId());
                    dto.setTitle(chapter.getTitle());
                    dto.setNumber(chapter.getNumber());
                    dto.setReleaseDate(chapter.getReleaseDate());
                    dto.setImages(chapter.getImages());
                    
                    if (chapter.getManwha() != null) {
                        dto.setManwhaTitle(chapter.getManwha().getTitle());
                        dto.setManwhaUrl(chapter.getManwha().getUrl());
                    }
                    
                    return ResponseEntity.ok(dto);
                })
                .orElse(ResponseEntity.notFound().build());
    }
    
    public static class ChapterDetailedResponse {
        private Long id;
        private String title;
        private Double number;
        private String releaseDate;
        private java.util.List<com.devtony.manwhaverse.manwhaverse.model.ChapterImage> images;
        private String manwhaTitle;
        private String manwhaUrl;
        
        // Getters and Setters
        public Long getId() { return id; }
        public void setId(Long id) { this.id = id; }
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        public Double getNumber() { return number; }
        public void setNumber(Double number) { this.number = number; }
        public String getReleaseDate() { return releaseDate; }
        public void setReleaseDate(String releaseDate) { this.releaseDate = releaseDate; }
        public java.util.List<com.devtony.manwhaverse.manwhaverse.model.ChapterImage> getImages() { return images; }
        public void setImages(java.util.List<com.devtony.manwhaverse.manwhaverse.model.ChapterImage> images) { this.images = images; }
        public String getManwhaTitle() { return manwhaTitle; }
        public void setManwhaTitle(String manwhaTitle) { this.manwhaTitle = manwhaTitle; }
        public String getManwhaUrl() { return manwhaUrl; }
        public void setManwhaUrl(String manwhaUrl) { this.manwhaUrl = manwhaUrl; }
    }
}
