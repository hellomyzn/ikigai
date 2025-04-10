from repositories.org.book import GssBookRepository
from models.org import Book

class BookService:
    def __init__(self):
        self.book_repository = GssBookRepository()

    def get_books(self):
        return self.book_repository.all()

    def save(self, books: list[Book,]):
            
        # それをリポジトリに渡して保存
        self.book_repository.add(books)
