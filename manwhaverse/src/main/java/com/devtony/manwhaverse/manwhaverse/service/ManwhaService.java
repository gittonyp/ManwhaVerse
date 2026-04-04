package com.devtony.manwhaverse.manwhaverse.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.devtony.manwhaverse.manwhaverse.model.Manwha;
import com.devtony.manwhaverse.manwhaverse.repository.ManwhaRepository;

@Service
public class ManwhaService {

    @Autowired
    private ManwhaRepository manwhaRepository;

    public Manwha getFeaturedManwha() {
        // For now, just return the first one found or random.
        // In a real app, this would query based on a flag or logic.
        List<Manwha> all = manwhaRepository.findAll();
        if (all.isEmpty()) return null;
        return all.get(0);
    }

    public List<Manwha> getPopularManwhas() {
        // Return all for now, maybe top 10.
        // Should implement sorting by views in Repository later.
        return manwhaRepository.findAll();
    }

    public Optional<Manwha> getManwhaDetails(String id) {
        // ID is the URL suffix
        return manwhaRepository.findById(id);
    }

    
    public List<Manwha> searchManwha(String title) {
        List<Manwha> result=manwhaRepository.searchByTitle(title.trim());
        return result;
    }

    public byte[] getBannerById(String id) {
        // TODO Auto-generated method stub
        return manwhaRepository.findById(id)
            .map(manwha -> manwha.getImageshow())
            .orElse(null);

    }

    
}
