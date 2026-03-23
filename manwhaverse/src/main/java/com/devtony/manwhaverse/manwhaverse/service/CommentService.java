package com.devtony.manwhaverse.manwhaverse.service;

import com.devtony.manwhaverse.manwhaverse.entity.Comment;
import com.devtony.manwhaverse.manwhaverse.entity.User;
import com.devtony.manwhaverse.manwhaverse.repository.CommentRepository;
import com.devtony.manwhaverse.manwhaverse.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CommentService {
    
    @Autowired
    private CommentRepository commentRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    public List<Comment> getComments(String mangaUrl, Long chapterId) {
        if (chapterId == null) {
            return commentRepository.findByMangaUrlAndChapterIdIsNullOrderByCreatedAtDesc(mangaUrl);
        } else {
            // We use mangaUrl AND chapterId to be safe, but chapterId is unique PK.
            // Since chapterId is global PK of a chapter, we actually don't Strictly need mangaUrl if we trust chapterId,
            // but the table stores mangaUrl too. 
            // Wait, does "comments" table enforce consistent mangaUrl? Yes.
            return commentRepository.findByMangaUrlAndChapterIdOrderByCreatedAtDesc(mangaUrl, chapterId);
        }
    }
    
    public Comment addComment(Long userId, String mangaUrl, String content, Long chapterId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
                
        Comment comment = new Comment(user, mangaUrl, content, chapterId);
        return commentRepository.save(comment);
    }
}
