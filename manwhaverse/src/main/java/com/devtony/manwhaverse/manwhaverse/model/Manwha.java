package com.devtony.manwhaverse.manwhaverse.model;

import jakarta.persistence.*;
import java.util.List;

@Entity
@Table(name = "manga")
@SecondaryTable(name = "manga_details", pkJoinColumns = @PrimaryKeyJoinColumn(name = "manga_url", referencedColumnName = "url"))
public class Manwha {

    @Id
    @Column(name = "url", nullable = false, unique = true)
    private String url;

    @Column(name = "title")
    private String title;

    @Column(name = "last_chapter")
    private Integer lastChapter;

    // --- Sidecar Table Fields ---

    @Column(table = "manga_details", name = "description")
    private String description;

    @Column(table = "manga_details", name = "banner_image")
    private String bannerImage;

    @Column(table = "manga_details", name = "author")
    private String author;

    @Column(table = "manga_details", name = "status")
    private String status;

    @Column(table = "manga_details", name = "views")
    private String views;

    @Column(table = "manga_details", name = "genres")
    private String genres; // Comma separated string

    @OneToMany(mappedBy = "manwha", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Chapter> chapters;

    // Getters and Setters
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public Integer getLastChapter() { return lastChapter; }
    public void setLastChapter(Integer lastChapter) { this.lastChapter = lastChapter; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getBannerImage() { return bannerImage; }
    public void setBannerImage(String bannerImage) { this.bannerImage = bannerImage; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getViews() { return views; }
    public void setViews(String views) { this.views = views; }

    public String getGenres() { return genres; }
    public void setGenres(String genres) { this.genres = genres; }

    public List<Chapter> getChapters() { return chapters; }
    public void setChapters(List<Chapter> chapters) { this.chapters = chapters; }
}
