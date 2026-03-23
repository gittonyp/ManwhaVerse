package com.devtony.manwhaverse.manwhaverse.service;

import com.devtony.manwhaverse.manwhaverse.model.Chapter;
import com.devtony.manwhaverse.manwhaverse.repository.ChapterRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ChapterService {

    @Autowired
    private ChapterRepository chapterRepository;

    public List<Chapter> getChaptersByManwha(String manwhaId) {
        return chapterRepository.findByManwhaUrlOrderByNumberDesc(manwhaId);
    }

    public Optional<Chapter> getChapterDetails(Long id) {
        return chapterRepository.findById(id);
    }
}
