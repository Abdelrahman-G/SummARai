package com.summarai.summarai.service;

import com.summarai.summarai.dto.BookSummaryDto;
import com.summarai.summarai.dto.SummaryDto;

import com.summarai.summarai.dto.BookSearchRequest;
import com.summarai.summarai.dto.UserSummaryDto;
import com.summarai.summarai.model.BookSummary;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

public interface SummaryService {
    public List<BookSummary> saveBooks(List<BookSummaryDto> bookSummaries, List<MultipartFile> file);
    public BookSummary saveBook(BookSummaryDto bookSummaries,MultipartFile files) throws IOException;
    public Page<BookSummaryDto> getAllBooks(Pageable pageable);
    public Page<BookSummaryDto> getBooksByGenre(String genre, Pageable pageable);
//    public void normalizeExistingBooks();
    public Optional<SummaryDto> getBookById(Long id);

    public Page<BookSummaryDto> getBooksByAuthor(String author, Pageable pageable);

    public Page<BookSummaryDto> getBooksByTitle(String title, Pageable pageable);

    public Page<?> searchBooks(BookSearchRequest criteria, Pageable pageable);
    public String getSummaryURL(Long id);
    public Page<UserSummaryDto> getMySummaries(Pageable pageable);
    public boolean updateSummaryStatus(Long summaryId, Boolean status);
}
