package com.devtony.manwhaverse.manwhaverse.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.devtony.manwhaverse.manwhaverse.model.Chapter;
import com.devtony.manwhaverse.manwhaverse.model.Manwha;
import com.devtony.manwhaverse.manwhaverse.service.ChapterService;
import com.devtony.manwhaverse.manwhaverse.service.ManwhaService;

@RestController
@RequestMapping("/api/manwhas")
public class ManwhaController {

    @Autowired
    private ManwhaService manwhaService;

    @Autowired
    private ChapterService chapterService;

    @GetMapping("/featured")
    public ResponseEntity<Manwha> getFeatured() {
        Manwha featured = manwhaService.getFeaturedManwha();
        if (featured == null) return ResponseEntity.notFound().build();
        return ResponseEntity.ok(featured);
    }

    @GetMapping("/popular")
    public ResponseEntity<List<Manwha>> getPopular() {
        return ResponseEntity.ok(manwhaService.getPopularManwhas());
    }

    @GetMapping("/search/{title}")
    public ResponseEntity<List<Manwha>> getSearch(@PathVariable String title) {
        List<Manwha> searchResult = manwhaService.searchManwha(title);
        return ResponseEntity.ok(searchResult);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Manwha> getDetails(@PathVariable String id) {
        return manwhaService.getManwhaDetails(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // Fallback/Alternative using Query Param
    @GetMapping("/details")
    public ResponseEntity<Manwha> getDetailsByQuery(@RequestParam String id) {
        return manwhaService.getManwhaDetails(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/{id}/chapters")
    public ResponseEntity<List<Chapter>> getChapters(@PathVariable String id) {
        List<Chapter> chapters = chapterService.getChaptersByManwha(id);
        return ResponseEntity.ok(chapters);
    }

    // Fallback/Alternative using Query Param
    @GetMapping("/chapters")
    public ResponseEntity<List<Chapter>> getChaptersByQuery(@RequestParam String id) {
        List<Chapter> chapters = chapterService.getChaptersByManwha(id);
        return ResponseEntity.ok(chapters);
    }


}
