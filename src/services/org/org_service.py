"""services.org.org_service"""
from typing import List, Tuple, Dict
from googleapiclient.errors import HttpError
from repositories.org import OrgReader
from repositories.org.book import GssBookRepository, CsvBookRepository
from repositories.org.book_log import GssBookLogRepository, CsvBookLogRepository
from repositories.org.book_clock_log import GssBookClockLogRepository, CsvBookClockLogRepository
from repositories.google_calendar_event_repository import GoogleCalendarEventRepository
from models.org import Book, BookLog, BookClockLog
from common.config import Config
from common.log import info, warn, error_stack_trace

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

        # GSSリポジトリ
        self.gss_book_repository = GssBookRepository()
        self.gss_book_log_repository = GssBookLogRepository()
        self.gss_book_clock_log_repository = GssBookClockLogRepository()

        # Google Calendarリポジトリ
        config = Config().config
        calendar_id = config['CALENDAR']['CALENDAR_ID']
        self.calendar_repository = GoogleCalendarEventRepository(calendar_id)

    def get_books(self) -> Tuple[List[Book], List[BookLog], List[BookClockLog]]:
        """本・本ログ・本クロックログの一覧を取得する"""
        books_dict_from_org, logs_dict_from_org, clocks_dict_from_org = self.reader.load_books()

        existing_books_dict = self.csv_book_repository.all()
        existing_logs_dict = self.csv_book_log_repository.all()
        existing_clocks_dict = self.csv_book_clock_log_repository.all()

        next_book_id = self.csv_book_repository.find_next_id()
        next_log_id = self.csv_book_log_repository.find_next_id()
        next_clock_id = self.csv_book_clock_log_repository.find_next_id()

        book_id_map = self._create_book_id_map(existing_books_dict)
        new_books, updated_book_id_map = self._process_new_books(
            books_dict_from_org, existing_books_dict, next_book_id, book_id_map
        )

        new_logs = self._process_new_logs(logs_dict_from_org, updated_book_id_map, next_log_id)
        new_clocks = self._process_new_clocks(clocks_dict_from_org, updated_book_id_map, next_clock_id)

        books = [Book.from_dict(b) for b in new_books]
        book_logs = [BookLog.from_dict(l) for l in new_logs]
        book_clock_logs = [BookClockLog.from_dict(c) for c in new_clocks]

        return books, book_logs, book_clock_logs

    def save(self, books: List[Book], book_logs: List[BookLog], book_clock_logs: List[BookClockLog]) -> None:
        """本・本ログ・本クロックログを保存する"""
        try:
            # CSVに保存
            self.csv_book_repository.add(books)
            self.gss_book_repository.add(books)
            info(f"Saved {len(books)} books to CSV")
            self.csv_book_log_repository.add(book_logs)
            self.gss_book_log_repository.add(book_logs)
            info(f"Saved {len(book_logs)} book logs to CSV")
            self.csv_book_clock_log_repository.add(book_clock_logs)
            self.gss_book_clock_log_repository.add(book_clock_logs)
            info(f"Saved {len(book_clock_logs)} book clock logs to CSV")

            # Google Calendarに同期
            if book_logs or book_clock_logs:
                info("Starting Google Calendar sync")
                self.calendar_repository.add(book_logs, book_clock_logs)
                info(f"Synced {len(book_logs)} book logs and {len(book_clock_logs)} book clock logs to Google Calendar")
            else:
                info("No new logs or clock logs to sync to Google Calendar")

        except HttpError as exc:
            warn(f"Failed to sync to Google Calendar: {exc}")
            error_stack_trace(f"Google Calendar sync error: {exc}")
            # エラーをログに記録し、処理を続行（CSV保存は保持）
        except Exception as exc:
            error_stack_trace(f"Unexpected error in save: {exc}")
            raise  # その他のエラーは再スロー

    def sync_to_google_calendar(self) -> None:
        """新しいデータを取得し、Google Calendarに同期"""
        try:
            books, book_logs, book_clock_logs = self.get_books()
            if book_logs or book_clock_logs:
                info("Starting Google Calendar sync for new data")
                self.calendar_repository.add(book_logs, book_clock_logs)
                info(f"Synced {len(book_logs)} book logs and {len(book_clock_logs)} book clock logs to Google Calendar")
            else:
                info("No new data to sync to Google Calendar")
        except HttpError as exc:
            warn(f"Failed to sync to Google Calendar: {exc}")
            error_stack_trace(f"Google Calendar sync error: {exc}")
        except Exception as exc:
            error_stack_trace(f"Unexpected error in sync_to_google_calendar: {exc}")
            raise

    def _create_book_id_map(self, existing_books: List[Dict]) -> Dict:
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
        books_from_org: List[Dict],
        existing_books: List[Dict],
        next_book_id: int,
        book_id_map: Dict
    ) -> Tuple[List[Dict], Dict]:
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
        logs_from_org: List[Dict],
        book_id_map: Dict,
        next_log_id: int
    ) -> List[Dict]:
        """新しいBookLogデータを抽出し、book_idとidを割り当てる"""
        new_logs = []
        current_log_id = next_log_id

        compare_keys = ["state", "from_status", "timestamp"]
        for log in logs_from_org:
            book = log.pop("book")
            book_key = (book["title"], book["url"], book["created_at"])
            book_id = book_id_map.get(book_key)

            if book_id is None:
                continue

            log_key = tuple(log.get(k) for k in compare_keys) + (book_id,)
            if not self._is_existing_log(log_key, book_id):
                log["id"] = current_log_id
                log["book_id"] = book_id
                new_logs.append(log)
                current_log_id += 1

        return new_logs

    def _process_new_clocks(
        self,
        clocks_from_org: List[Dict],
        book_id_map: Dict,
        next_clock_id: int
    ) -> List[Dict]:
        """新しいBookClockLogデータを抽出し、book_idとidを割り当てる"""
        new_clocks = []
        current_clock_id = next_clock_id

        compare_keys = ["clock_start", "clock_end"]
        for clock in clocks_from_org:
            book = clock.pop("book")
            book_key = (book["title"], book["url"], book["created_at"])
            book_id = book_id_map.get(book_key)

            if book_id is None:
                continue

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