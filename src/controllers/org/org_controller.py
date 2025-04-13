"""controller/org/org_controller"""
from services.org.org_service import OrgService
from models.org import Book, BookLog, BookClockLog


class OrgController:
    """OrgController - 本に関連する操作を管理する"""
    org_service = OrgService()

    @classmethod
    def get_books_from_org(cls) -> list[Book]:
        """orgファイルからBookデータを抽出する"""
        return cls.org_service.get_books()

    @classmethod
    def save_books(cls, books: list[Book],
                   book_logs: list[BookLog],
                   book_clock_logs: list[BookClockLog]) -> None:
        """本・本ログ・本クロックログを保存する"""
        cls.org_service.save(books, book_logs, book_clock_logs)