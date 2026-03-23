package com.devtony.manwhaverse.manwhaverse.repository;

import com.devtony.manwhaverse.manwhaverse.entity.Comment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {
    
    List<Comment> findByMangaUrlAndChapterIdIsNullOrderByCreatedAtDesc(String mangaUrl);
    
    List<Comment> findByMangaUrlAndChapterIdOrderByCreatedAtDesc(String mangaUrl, Long chapterId);
}
