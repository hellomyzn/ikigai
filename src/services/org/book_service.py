"""services.org.book_service"""
from repositories.org.book import GssBookRepository, CsvBookRepository
from repositories.org.book_log import GssBookLogRepository, CsvBookLogRepository
from repositories.org.book_clock_log import GssBookClockLogRepository, CsvBookClockLogRepository
from models.org import Book, BookLog, BookClockLog

class BookService:
    """BookService - 本に関連するサービス"""
    def __init__(self):
        # gss
        self.gss_book_repository = GssBookRepository()
        self.gss_book_log_repository = GssBookLogRepository()
        self.gss_book_clock_log_repository = GssBookClockLogRepository()

        # csv
        self.csv_book_repository = CsvBookRepository()
        self.csv_book_log_repository = CsvBookLogRepository()
        self.csv_book_clock_log_repository = CsvBookClockLogRepository()

    def get_books(self) -> tuple[list[Book], list[BookLog], list[BookClockLog]]:
        """本・本ログ・本クロックログの一覧を取得する

        Returns:
            tuple[list[Book], list[BookLog], list[BookClockLog]]: 取得したデータのタプル
        """
        books = self.gss_book_repository.all()
        book_logs = self.gss_book_log_repository.all()
        book_clock_logs = self.gss_book_clock_log_repository.all()
        return books, book_logs, book_clock_logs

    def save(self, books: list[Book],
             book_logs: list[BookLog],
             book_clock_logs: list[BookClockLog]) -> None:
        """本・本ログ・本クロックログを保存する

        Args:
            books (list[Book]): 本データのリスト
            book_logs (list[BookLog]): 本ログデータのリスト
            book_clock_logs (list[BookClockLog]): 本クロックログデータのリスト
        """

        self.csv_book_repository.add(books)
        self.csv_book_log_repository.add(book_logs)
        self.csv_book_clock_log_repository.add(book_clock_logs)

        # self.book_repository.add(books)
        # self.book_log_repository.add(book_logs)
        # self.book_clock_log_repository.add(book_clock_logs)
