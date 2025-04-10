from services.org import BookService
from models.org import Book

class OrgController:
    def __init__(self):
        self.book_service = BookService()

    def get_books(self):
        return self.book_service.get_books()

    def save_book(self, books: list[Book,]):
        return self.book_service.save(books)
