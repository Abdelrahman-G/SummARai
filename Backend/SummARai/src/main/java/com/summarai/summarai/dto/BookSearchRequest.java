package com.summarai.summarai.dto;

import java.util.List;

public class BookSearchRequest {
    private String author;
    private String title;
    private List<String> genres;

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public List<String> getGenres() { return genres; }
    public void setGenres(List<String> genres) { this.genres = genres; }

}