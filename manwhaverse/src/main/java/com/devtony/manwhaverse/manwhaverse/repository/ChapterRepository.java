package com.devtony.manwhaverse.manwhaverse.repository;

import com.devtony.manwhaverse.manwhaverse.model.Chapter;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChapterRepository extends JpaRepository<Chapter, Long> {
    List<Chapter> findByManwhaUrlOrderByNumberDesc(String manwhaUrl);
}
