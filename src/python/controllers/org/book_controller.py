"""controller/org/book_controller"""
from services.org.book_service import BookService
from models.org import Book, BookLog, BookClockLog

class BookController:
    """BookController - 本に関連する操作を管理する"""
    book_service = BookService()

    @classmethod
    def get_books(cls) -> tuple[list[Book], list[BookLog], list[BookClockLog]]:
        """本・本ログ・本クロックログを取得する"""
        return cls.book_service.get_books()

    @classmethod
    def save_books(cls, books: list[Book],
                   book_logs: list[BookLog],
                   book_clock_logs: list[BookClockLog]) -> None:
        """本・本ログ・本クロックログを保存する"""
        cls.book_service.save(books, book_logs, book_clock_logs)