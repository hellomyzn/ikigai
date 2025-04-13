"""repositories.google_calendar_base_repository"""
from abc import ABC, abstractmethod
from typing import List
from googleapiclient.errors import HttpError

from common.config import Config
from common.google_calendar import GoogleCalendarAccessor
from common.log import warn, info, debug
from models import Model

CONFIG = Config().config
IS_OFFLINE = CONFIG["APP"]["OFFLINE"]

class GoogleCalendarBase(ABC):
    """Google Calendarの基本操作を提供するベースクラス"""

    def __init__(self, calendar_id: str):
        self.calendar_id = calendar_id
        self.gcal = None
        if not IS_OFFLINE:
            self.gcal = GoogleCalendarAccessor()

    @abstractmethod
    def add(self, data: List[Model]) -> None:
        """データをGoogle Calendarに追加"""
        pass

    def _handle_error(self, exc: HttpError):
        """Google Calendar APIエラーをハンドリング"""
        try:
            err_status = exc.resp.status
            if err_status == 403:
                warn("Permission error for calendar {0}: {1}", self.calendar_id, exc)
                raise PermissionError(f"Insufficient permissions for calendar {self.calendar_id}") from exc
            elif err_status == 429:
                warn("Rate limit exceeded for calendar {0}: {1}", self.calendar_id, exc)
                raise RuntimeError("Rate limit exceeded") from exc
            else:
                warn("Google Calendar API error for calendar {0}: {1}", self.calendar_id, exc)
                raise RuntimeError(f"API error: {exc}") from exc
        except AttributeError:
            warn("Unexpected error for calendar {0}: {1}", self.calendar_id, exc)
            raise