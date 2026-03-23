package com.devtony.manwhaverse.manwhaverse.model;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonIgnore;
import java.util.List;

@Entity
@Table(name = "chapters")
public class Chapter {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "title")
    private String title;

    @Column(name = "number")
    private Double number;

    @Column(name = "release_date")
    private String releaseDate;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "manga_url", referencedColumnName = "url")
    @JsonIgnore
    private Manwha manwha;

    @OneToMany(mappedBy = "chapter", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<ChapterImage> images;

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public Double getNumber() { return number; }
    public void setNumber(Double number) { this.number = number; }

    public String getReleaseDate() { return releaseDate; }
    public void setReleaseDate(String releaseDate) { this.releaseDate = releaseDate; }

    public Manwha getManwha() { return manwha; }
    public void setManwha(Manwha manwha) { this.manwha = manwha; }

    public List<ChapterImage> getImages() { return images; }
    public void setImages(List<ChapterImage> images) { this.images = images; }
}
