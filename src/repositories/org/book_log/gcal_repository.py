"""repositories.org.book_log.gc_repository"""
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from models.org import BookLog
from repositories.google_calendar_base_repository import GoogleCalendarBaseRepository
from repositories.org.book import CsvBookRepository
from common.log import warn
from common.config import Config

class GcalBookLogRepository(GoogleCalendarBaseRepository):
    """Google CalendarにBookLogを追加するリポジトリ"""
    __config = Config().config
    __cal_id = __config['CALENDAR']['CALENDAR_ID']

    def __init__(self):
        __config = Config().config
        __cal_id = __config['CALENDAR']['CALENDAR_ID']
        event_type = "log"

        super().__init__(__cal_id, event_type)
        self.book_repository = CsvBookRepository()

    def _build_event(self, item: BookLog) -> Dict[str, Any]:
        """BookLogからGoogle Calendarイベントを構築"""
        book = self.book_repository.find_by_id(item.book_id)
        if not book:
            warn(f"Book not found for book_id: {item.book_id}")
            return {}

        title = f"{item.state}: {book.get('title', '')}"
        desc = f"url: {book.get('url', '')}"
        try:
            start_time = datetime.strptime(item.timestamp, "%Y-%m-%d %H:%M")
            end_time = start_time + timedelta(minutes=10)
            start_dt = self._convert_to_google_datetime(start_time)
            end_dt = self._convert_to_google_datetime(end_time)
        except ValueError as exc:
            warn(f"Invalid timestamp for log_id={item.id}: {exc}")
            return {}

        event = {
            "summary": title,
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
                    "type": self.event_type,
                    "log_id": str(item.id),
                    "book_id": str(item.book_id),
                    "state": item.state
                }
            }
        }
        return event

    def _get_event_key(self, item: BookLog) -> Tuple:
        """BookLogの一意キーを取得"""
        dt = self._convert_to_google_datetime(item.timestamp)
        return (dt, item.state, item.book_id)

    def _extract_event_key(self, event: Dict,  props: Dict) -> Tuple:
        """イベントから一意キーを抽出（子クラスでカスタマイズ可能）"""
        return (
            event["start"].get("dateTime"),
            props.get("state", ""),
            int(props.get("book_id", -1))
        )
