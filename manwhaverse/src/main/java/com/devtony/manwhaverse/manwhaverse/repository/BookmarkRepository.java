package com.devtony.manwhaverse.manwhaverse.repository;

import com.devtony.manwhaverse.manwhaverse.entity.Bookmark;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookmarkRepository extends JpaRepository<Bookmark, Long> {
    
    List<Bookmark> findByUserId(Long userId);
    
    Optional<Bookmark> findByUserIdAndMangaUrl(Long userId, String mangaUrl);
    
    boolean existsByUserIdAndMangaUrl(Long userId, String mangaUrl);
    
    void deleteByUserIdAndMangaUrl(Long userId, String mangaUrl);
}
