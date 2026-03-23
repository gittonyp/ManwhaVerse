package com.devtony.manwhaverse.manwhaverse.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.devtony.manwhaverse.manwhaverse.model.Manwha;

@Repository
public interface ManwhaRepository extends JpaRepository<Manwha, String> {

    @Query("""
        SELECT m FROM Manwha m
        WHERE LOWER(m.title) LIKE LOWER(CONCAT('%', :title, '%'))
    """)
    List<Manwha> searchByTitle(@Param("title") String title);
    // List<Manwha> findByTitleContaining(String title);

    // List<Manwha> findByTitleContainingIgnoreCase(String title);

    // List<Manwha> findByTitleContaining(String title);
    // Basic JPA methods are enough.
    // Can add custom finders if needed.
    // List<Manwha> findByFeaturedTrue(); // If we had a featured flag
}
