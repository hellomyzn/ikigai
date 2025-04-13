"""repositories.google_calendar_event_repository"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError

from common.log import info, debug, warn
from common.config import Config
from models.org import Book, BookLog, BookClockLog
from repositories.google_calendar_base_repository import GoogleCalendarBase
from repositories.org.book import CsvBookRepository

CONFIG = Config().config
IS_OFFLINE = CONFIG["APP"]["OFFLINE"]

class GoogleCalendarEventRepository(GoogleCalendarBase):
    """Google CalendarにBookLogとBookClockLogのイベントを追加するリポジトリ"""

    def __init__(self, calendar_id: str = "primary"):
        super().__init__(calendar_id)
        self.book_repository = CsvBookRepository()

    def add(self, book_logs: List[BookLog], book_clock_logs: List[BookClockLog]) -> None:
        """BookLogとBookClockLogをGoogle Calendarイベントとして追加"""
        if IS_OFFLINE:
            warn("Adding events doesn't work in offline mode")
            return

        # BookLogイベント
        for log in book_logs:
            self._create_log_event(log)

        # BookClockLogイベント

        for clock in book_clock_logs:
            self._create_clock_event(clock)

    def _create_log_event(self, log: BookLog) -> None:
        """BookLogから5分間のGoogle Calendarイベントを作成"""
        book = self.book_repository.find_by_id(log.book_id)
        if not book:
            warn(f"Book not found for book_id: {log.book_id}")
            return

        event_key = (log.timestamp, log.state, log.book_id)
        if self._event_exists(event_key, "log"):
            debug(f"Log event already exists: log_id={log.id}")
            return

        try:
            desc = f"url: {book.get('url', '')}"
            start_time = datetime.strptime(log.timestamp, "%Y-%m-%d %H:%M")
            end_time = start_time + timedelta(minutes=5)
            start_dt = self.__convert_to_google_datetime(log.timestamp)
            end_dt = self.__convert_to_google_datetime(end_time)
            event = {
                "summary": f"{log.state}: {book['title']}",
                "description": desc,
                "start": {
                    "dateTime": start_dt,
                    "timeZone": "Asia/Tokyo"
                },
                "end": {
                    "dateTime": end_dt,
                    "timeZone": "Asia/Tokyo"
                },
                "extendedProperties": {
                    "private": {
                        "type": "log",
                        "log_id": str(log.id),
                        "book_id": str(log.book_id)
                    }
                }
            }
            self.gcal.connection.events().insert(calendarId=self.calendar_id, body=event).execute()
            info(f"Created log event: log_id={log.id}, book_id={log.book_id}")
        except HttpError as exc:
            self._handle_error(exc)

    def _create_clock_event(self, clock: BookClockLog) -> None:
        """BookClockLogからGoogle Calendarイベントを作成"""
        book = self.book_repository.find_by_id(clock.book_id)
        if not book:
            warn(f"Book not found for book_id: {clock.book_id}")
            return

        event_key = (clock.clock_start, clock.clock_end, clock.book_id)
        if self._event_exists(event_key, "clock"):
            info(f"Clock event already exists: clock_id={clock.id}")
            return

        try:
            desc = f"url: {book.get('url', '')}"
            start_dt = self.__convert_to_google_datetime(clock.clock_start)
            end_dt = self.__convert_to_google_datetime(clock.clock_end)
            event = {
                "summary": book["title"],
                "description": desc,
                "start": {
                    "dateTime": start_dt,
                    "timeZone": "Asia/Tokyo"
                },
                "end": {
                    "dateTime": end_dt,
                    "timeZone": "Asia/Tokyo"
                },
                "extendedProperties": {
                    "private": {
                        "type": "clock",
                        "clock_id": str(clock.id),
                        "book_id": str(clock.book_id)
                    }
                }
            }
            self.gcal.connection.events().insert(calendarId=self.calendar_id, body=event).execute()
            info(f"Created clock event: clock_id={clock.id}, book_id={clock.book_id}")
        except HttpError as exc:
            self._handle_error(exc)

    def _event_exists(self, event_key: Tuple, event_type: str) -> bool:
        """イベントがGoogle Calendarに存在するかチェック"""
        try:
            events = self.gcal.connection.events().list(
                calendarId=self.calendar_id,
                privateExtendedProperty=f"type={event_type}",
                maxResults=1000
            ).execute()
            for event in events.get("items", []):
                props = event.get("extendedProperties", {}).get("private", {})
                if event_type == "clock":
                    stored_key = (
                        event["start"].get("dateTime"),
                        event["end"].get("dateTime"),
                        int(props.get("book_id", -1))
                    )
                else:  # log
                    stored_key = (
                        event["start"].get("dateTime"),
                        props.get("state", ""),
                        int(props.get("book_id", -1))
                    )
                if stored_key == event_key:
                    return True
        except HttpError as exc:
            self._handle_error(exc)
        return False

    def __convert_to_google_datetime(self, dt: str | datetime) -> str:
        if isinstance(dt, str):
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M")
        return dt.isoformat(timespec="seconds") + "+09:00"