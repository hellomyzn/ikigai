"""repositories.org.book_clock_log.gc_repository"""
from typing import Dict, Any, Tuple
from datetime import datetime
from models.org import BookClockLog
from repositories.google_calendar_base_repository import GoogleCalendarBaseRepository
from repositories.org.book import CsvBookRepository
from common.log import warn
from common.config import Config

class GcalBookClockLogRepository(GoogleCalendarBaseRepository):
    """Google CalendarにBookClockLogを追加するリポジトリ"""
    __config = Config().config
    __cal_id = __config['CALENDAR']['CALENDAR_ID']


    def __init__(self, calendar_id: str = "primary"):
        __config = Config().config
        __cal_id = __config['CALENDAR']['CALENDAR_ID']
        event_type = "clock"

        super().__init__(__cal_id, event_type)
        self.book_repository = CsvBookRepository()

    def _build_event(self, item: BookClockLog) -> Dict[str, Any]:
        """BookClockLogからGoogle Calendarイベントを構築"""
        book = self.book_repository.find_by_id(item.book_id)
        if not book:
            warn(f"Book not found for book_id: {item.book_id}")
            return {}

        title = f"{book['title']}"
        desc = f"url: {book.get('url', '')}"

        try:
            start_time = datetime.strptime(item.clock_start, "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(item.clock_end, "%Y-%m-%d %H:%M")
            start_dt = self._convert_to_google_datetime(start_time)
            end_dt = self._convert_to_google_datetime(end_time)
        except ValueError as exc:
            warn(f"Invalid datetime for clock_id={item.id}: {exc}")
            return {}

        if start_time >= end_time:
            warn(f"Invalid clock log: clock_id={item.id}, start={item.clock_start} >= end={item.clock_end}")
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
                    "type": "clock",
                    "clock_id": str(item.id),
                    "book_id": str(item.book_id)
                }
            }
        }
        return event

    def _get_event_key(self, item: BookClockLog) -> Tuple:
        """BookClockLogの一意キーを取得"""
        start_dt = self._convert_to_google_datetime(item.clock_start)
        end_dt = self._convert_to_google_datetime(item.clock_end)
        return (start_dt, end_dt, item.book_id)

    def _extract_event_key(self, event, props):
        """イベントから一意キーを抽出（子クラスでカスタマイズ可能）"""
        return (
            event["start"].get("dateTime"),
            event["end"].get("dateTime"),
            int(props.get("book_id", -1))
        )
