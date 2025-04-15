"""repositories.google_calendar_base_repository"""
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from googleapiclient.errors import HttpError

from common.config import Config
from common.google_calendar import GoogleCalendarAccessor
from common.log import warn, info, debug
from models import Model

CONFIG = Config().config
IS_OFFLINE = CONFIG["APP"]["OFFLINE"]

class GoogleCalendarBaseRepository(ABC):
    """Google Calendarの基本操作を提供するベース抽象クラス"""

    def __init__(self, calendar_id: str, event_type: str):
        self.calendar_id = calendar_id
        self.event_type = event_type
        self.gcal = None
        if not IS_OFFLINE:
            self.gcal = GoogleCalendarAccessor()

    def add(self, items: List[Model]) -> None:
        """データをGoogle Calendarに追加"""
        if IS_OFFLINE:
            warn("Adding events doesn't work in offline mode")
            return

        for item in items:
            self._create_event(item)

    def _create_event(self, item: Model) -> bool:
        """Google Calendarイベントを作成"""
        event_data = self._build_event(item)
        if not event_data:
            warn(f"Failed to build event for item: {item}")
            return False

        event_key = self._get_event_key(item)
        if self._event_exists(event_key):
            info(f"Event already exists: {event_key}, type={self.event_type}")
            return False

        try:
            self.gcal.connection.events().insert(calendarId=self.calendar_id, body=event_data).execute()
            info(f"Created event: {event_key}, type={self.event_type}")
            return True
        except HttpError as exc:
            self._handle_error(exc)
            return False

    @abstractmethod
    def _build_event(self, item: Model) -> Dict[str, Any]:
        """子クラスでイベントデータを構築"""
        pass

    @abstractmethod
    def _get_event_key(self, item: Model) -> Tuple:
        """子クラスでイベントの一意キーを定義"""
        pass

    @abstractmethod
    def _extract_event_key(self, event: Dict, props: Dict) -> Tuple:
        """子クラスでイベントの一意キーを定義"""
        pass

    def _event_exists(self, event_key: Tuple) -> bool:
        """イベントがGoogle Calendarに存在するかチェック"""
        if not self.gcal:
            return False

        try:
            events = self.gcal.connection.events().list(
                calendarId=self.calendar_id,
                privateExtendedProperty=f"type={self.event_type}",
                maxResults=1000
            ).execute()
            for event in events.get("items", []):
                props = event.get("extendedProperties", {}).get("private", {})
                stored_key = self._extract_event_key(event, props)
                if stored_key == event_key:
                    return True
        except HttpError as exc:
            self._handle_error(exc)
        return False


    def _handle_error(self, exc: HttpError) -> None:
        """Google Calendar APIエラーをハンドリング"""
        try:
            err_status = exc.resp.status
            if err_status == 403:
                warn(f"Permission error for calendar {self.calendar_id}: {exc}")
                raise PermissionError(f"Insufficient permissions for calendar {self.calendar_id}") from exc
            elif err_status == 429:
                warn(f"Rate limit exceeded for calendar {self.calendar_id}: {exc}")
                raise RuntimeError("Rate limit exceeded") from exc
            else:
                warn(f"Google Calendar API error for calendar {self.calendar_id}: {exc}")
                raise RuntimeError(f"API error: {exc}") from exc
        except AttributeError:
            warn(f"Unexpected error for calendar {self.calendar_id}: {exc}")
            raise

    def _convert_to_google_datetime(self, dt: str | datetime) -> str:
        """日時をGoogle CalendarのRFC3339形式に変換"""
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M")
            except ValueError as exc:
                warn(f"Invalid datetime format: {dt}, error={exc}")
                raise
        return dt.isoformat(timespec="seconds") + "+09:00"