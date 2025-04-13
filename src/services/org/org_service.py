"""services.org.org_service"""
from typing import List, Tuple
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

        # CSVリポジトリ
        self.csv_book_repository = CsvBookRepository()
        self.csv_book_log_repository = CsvBookLogRepository()
        self.csv_book_clock_log_repository = CsvBookClockLogRepository()

        # GSSリポジトリ（未使用の場合はコメントアウト可能）
        self.gss_book_repository = GssBookRepository()
        self.gss_book_log_repository = GssBookLogRepository()
        self.gss_book_clock_log_repository = GssBookClockLogRepository()

    def get_books(self) -> Tuple[List[Book], List[BookLog], List[BookClockLog]]:
        """本・本ログ・本クロックログの一覧を取得する"""
        # Orgファイルからデータを取得
        books_dict_from_org, logs_dict_from_org, clocks_dict_from_org = self.reader.load_books()

        # 既存CSVデータを取得
        existing_books_dict = self.csv_book_repository.all()
        existing_logs_dict = self.csv_book_log_repository.all()
        existing_clocks_dict = self.csv_book_clock_log_repository.all()

        # 次のIDを取得
        next_book_id = self.csv_book_repository.find_next_id()
        next_log_id = self.csv_book_log_repository.find_next_id()
        next_clock_id = self.csv_book_clock_log_repository.find_next_id()

        # Bookのマッピング（title, url, created_at -> book_id）
        book_id_map = self._create_book_id_map(existing_books_dict)
        new_books, updated_book_id_map = self._process_new_books(
            books_dict_from_org, existing_books_dict, next_book_id, book_id_map
        )

        # BookLogとBookClockLogを処理
        new_logs = self._process_new_logs(logs_dict_from_org, updated_book_id_map, next_log_id)
        new_clocks = self._process_new_clocks(clocks_dict_from_org, updated_book_id_map, next_clock_id)

        # モデルに変換
        books = [Book.from_dict(b) for b in new_books]
        book_logs = [BookLog.from_dict(l) for l in new_logs]
        book_clock_logs = [BookClockLog.from_dict(c) for c in new_clocks]

        return books, book_logs, book_clock_logs

    def save(self, books: List[Book], book_logs: List[BookLog], book_clock_logs: List[BookClockLog]) -> None:
        """本・本ログ・本クロックログを保存する"""
        self.csv_book_repository.add(books)
        self.csv_book_log_repository.add(book_logs)
        self.csv_book_clock_log_repository.add(book_clock_logs)

        self.gss_book_repository.add(books)
        self.gss_book_log_repository.add(book_logs)
        self.gss_book_clock_log_repository.add(book_clock_logs)

    def _create_book_id_map(self, existing_books: List[dict]) -> dict[Tuple, int]:
        """既存のBookデータから(title, url, created_at) -> book_idのマッピングを作成"""
        book_id_map = {}
        for book in existing_books:
            key = (
                book.get("title"),
                book.get("url"),
                book.get("created_at")
            )
            book_id_map[key] = int(book["id"])
        return book_id_map

    def _process_new_books(
        self,
        books_from_org: List[dict],
        existing_books: List[dict],
        next_book_id: int,
        book_id_map: dict[Tuple, int]
    ) -> Tuple[List[dict], dict[Tuple, int]]:
        """新しいBookデータを抽出し、book_idを割り当てる"""
        new_books = []
        current_book_id = next_book_id

        compare_keys = ["title", "url", "created_at"]
        existing_set = {tuple(b.get(k) for k in compare_keys) for b in existing_books}

        for book in books_from_org:
            key = tuple(book.get(k) for k in compare_keys)
            if key not in existing_set:
                book["id"] = current_book_id
                new_books.append(book)
                book_id_map[key] = current_book_id
                current_book_id += 1

        return new_books, book_id_map

    def _process_new_logs(
        self,
        logs_from_org: List[dict],
        book_id_map: dict[Tuple, int],
        next_log_id: int
    ) -> List[dict]:
        """新しいBookLogデータを抽出し、book_idとidを割り当てる"""
        new_logs = []
        current_log_id = next_log_id

        compare_keys = ["state", "from_status", "timestamp"]
        for log in logs_from_org:
            book = log.pop("book")  # book情報を取り出す
            book_key = (book["title"], book["url"], book["created_at"])
            book_id = book_id_map.get(book_key)

            if book_id is None:
                continue  # 対応するBookがない場合はスキップ

            # 重複チェック
            log_key = tuple(log.get(k) for k in compare_keys) + (book_id,)
            if not self._is_existing_log(log_key, book_id):
                log["id"] = current_log_id
                log["book_id"] = book_id
                new_logs.append(log)
                current_log_id += 1

        return new_logs

    def _process_new_clocks(
        self,
        clocks_from_org: List[dict],
        book_id_map: dict[Tuple, int],
        next_clock_id: int
    ) -> List[dict]:
        """新しいBookClockLogデータを抽出し、book_idとidを割り当てる"""
        new_clocks = []
        current_clock_id = next_clock_id

        compare_keys = ["clock_start", "clock_end"]
        for clock in clocks_from_org:
            book = clock.pop("book")  # book情報を取り出す
            book_key = (book["title"], book["url"], book["created_at"])
            book_id = book_id_map.get(book_key)

            if book_id is None:
                continue  # 対応するBookがない場合はスキップ

            # 重複チェック
            clock_key = tuple(clock.get(k) for k in compare_keys) + (book_id,)
            if not self._is_existing_clock(clock_key, book_id):
                clock["id"] = current_clock_id
                clock["book_id"] = book_id
                new_clocks.append(clock)
                current_clock_id += 1

        return new_clocks

    def _is_existing_log(self, log_key: Tuple, book_id: int) -> bool:
        """BookLogが既存データに含まれるかチェック"""
        existing_logs = self.csv_book_log_repository.all()
        for existing in existing_logs:
            existing_key = (
                existing["state"],
                existing["from_status"],
                existing["timestamp"],
                int(existing["book_id"])
            )
            if existing_key == log_key:
                return True
        return False

    def _is_existing_clock(self, clock_key: Tuple, book_id: int) -> bool:
        """BookClockLogが既存データに含まれるかチェック"""
        existing_clocks = self.csv_book_clock_log_repository.all()
        for existing in existing_clocks:
            existing_key = (
                existing["clock_start"],
                existing["clock_end"],
                int(existing["book_id"])
            )
            if existing_key == clock_key:
                return True
        return False