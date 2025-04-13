"""services.org.org_service"""
from repositories.org import OrgReader
from repositories.org.book import GssBookRepository, CsvBookRepository
from repositories.org.book_log import GssBookLogRepository, CsvBookLogRepository
from repositories.org.book_clock_log import GssBookClockLogRepository, CsvBookClockLogRepository
from models.org import Book, BookLog, BookClockLog
from models import Model

class OrgService:
    """OrgService - 本に関連するサービス"""
    def __init__(self):
        org_file_paths = [
            "/opt/org/agendas/journal.org", 
            "/opt/org/agendas/tasks.org",
            "/opt/org/agendas/habits.org"
        ]
        self.reader = OrgReader(org_file_paths)

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

        (books_dict_from_org,
         logs_dict_from_org,
         clocks_dict_from_org) = self.reader.load_books()

        existing_books_dict = self.csv_book_repository.all()
        existing_logs_dict = self.csv_book_log_repository.all()
        existing_clock_dict = self.csv_book_clock_log_repository.all()

        # 3. 比較キーを指定
        compare_keys_of_books = ["title", "created_at", "url"]
        compare_keys_of_logs = ["title", "created_at", "url"]
        compare_keys_of_clocks = ["title", "created_at", "url"]

        # 4. 新規データだけ抽出
        new_books = self.filter_new_dicts(existing_books_dict, books_dict_from_org, compare_keys_of_books)
        print(new_books)
        ljl

        books = [Book.from_dict(d) for d in new_books]
        book_logs = [BookLog.from_dict(d) for d in book_logs_dict]
        book_clock_logs = [BookClockLog.from_dict(d) for d in book_clock_logs_dict]

        existing_books = self.csv_book_repository.all()

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

    def __assign_ids(self, books: list[Book],
                    book_logs: list[BookLog],
                    book_clock_logs: list[BookClockLog]) -> None:
        """リストにIDを付与する内部メソッド"""

        # 次に使うべきIDを取得
        next_book_id = self.csv_book_repository.find_next_id()
        next_book_log_id = self.csv_book_log_repository.find_next_id()
        next_book_clock_log_id = self.csv_book_clock_log_repository.find_next_id()

        # booksにIDを付与
        for idx, book in enumerate(books):
            book.id = next_book_id + idx

        # book_logsにIDを付与
        for idx, book_log in enumerate(book_logs):
            book_log.id = next_book_log_id + idx

        # book_clock_logsにIDを付与
        for idx, book_clock_log in enumerate(book_clock_logs):
            book_clock_log.id = next_book_clock_log_id + idx

    @staticmethod
    def filter_new_dicts(
        existing_dicts: list[dict],
        new_dicts: list[dict],
        compare_keys: list[str],
    ) -> list[dict]:
        """既存データと新規データを比較して、新規だけ返す（dict版）"""
        existing_set = set()

        # 既存データから比較用のセットを作る
        for record in existing_dicts:
            key_tuple = tuple(record.get(key) for key in compare_keys)
            existing_set.add(key_tuple)

        new_records = []
        for record in new_dicts:
            key_tuple = tuple(record.get(key) for key in compare_keys)
            if key_tuple not in existing_set:
                new_records.append(record)

        return new_records