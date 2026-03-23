package com.devtony.manwhaverse.manwhaverse.service;

import com.devtony.manwhaverse.manwhaverse.entity.Bookmark;
import com.devtony.manwhaverse.manwhaverse.model.Manwha;
import com.devtony.manwhaverse.manwhaverse.repository.BookmarkRepository;
import com.devtony.manwhaverse.manwhaverse.repository.ManwhaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class BookmarkService {
    
    @Autowired
    private BookmarkRepository bookmarkRepository;
    
    @Autowired
    private ManwhaRepository manwhaRepository;
    
    public List<Manwha> getUserBookmarks(Long userId) {
        List<Bookmark> bookmarks = bookmarkRepository.findByUserId(userId);
        
        if (bookmarks.isEmpty()) {
            return Collections.emptyList();
        }
        
        List<String> mangaUrls = bookmarks.stream()
                .map(Bookmark::getMangaUrl)
                .collect(Collectors.toList());
        
        return manwhaRepository.findAllById(mangaUrls);
    }
    
    @Transactional
    public boolean toggleBookmark(Long userId, String mangaUrl) {
        Optional<Bookmark> existing = bookmarkRepository.findByUserIdAndMangaUrl(userId, mangaUrl);
        
        if (existing.isPresent()) {
            bookmarkRepository.delete(existing.get());
            return false; // Removed
        } else {
            Bookmark bookmark = new Bookmark(userId, mangaUrl);
            bookmarkRepository.save(bookmark);
            return true; // Added
        }
    }
    
    public boolean isBookmarked(Long userId, String mangaUrl) {
        return bookmarkRepository.existsByUserIdAndMangaUrl(userId, mangaUrl);
    }
}
