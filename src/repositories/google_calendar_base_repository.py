"""repositories.google_calendar_base_repository"""
#########################################################
# Builtin packages
#########################################################
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Final
#########################################################
# 3rd party packages
#########################################################
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential

#########################################################
# Own packages
#########################################################
from common.config import Config
from common.google_calendar import GoogleCalendarAccessor
from common.log import warn, info
from common.exceptions import (GoogleCalendarPermissionError,
                               GoogleCalendarRateLimitError,
                               GoogleCalendarError)
from models import Model

DEFAULT_TIMEZONE: Final[str] = "Asia/Tokyo"
MAX_EVENT_RESULTS: Final[int] = 1000
EVENT_TYPE_KEY: Final[str] = "type"


class GoogleCalendarBaseRepository(ABC):
    """Google Calendarの基本操作を提供する抽象基底クラス。

    Args:
        calendar_id: 操作対象のGoogle Calendar ID。
        event_type: イベントのタイプ（例: 'log', 'clock'）。
        gcal_accessor: Google Calendar APIアクセサ。デフォルトはNone。
    """

    def __init__(self, calendar_id: str, event_type: str, gcal_accessor: GoogleCalendarAccessor | None = None):
        self._calendar_id = calendar_id
        self._event_type = event_type
        self._config = Config().config
        self._is_offline = self._config["APP"]["OFFLINE"]
        self._gcal = None
        if not self._is_offline:
            self._gcal = gcal_accessor if gcal_accessor else GoogleCalendarAccessor()

    def add(self, items: list[Model]) -> None:
        """Google Calendarにイベントを追加する。

        Args:
            items: 追加するイベントのモデルリスト。

        Raises:
            RuntimeError: オフラインモードで操作が試みられた場合。
        """
        if self._is_offline:
            warn("Cannot add events in offline mode")
            return
        for item in items:
            self._create_calendar_event(item)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=30, max=60))
    def _create_calendar_event(self, item: Model) -> bool:
        """Google Calendarに単一のイベントを作成する。

        Args:
            item: イベントのモデル。

        Returns:
            bool: イベント作成が成功した場合はTrue、失敗または既存の場合はFalse。

        Raises:
            GoogleCalendarError: APIエラーや権限エラーが発生した場合。
        """
        event_data = self._build_event(item)
        if not event_data:
            warn("Failed to build event. item: {0}", item)
            return False

        event_key = self._get_event_key(item)
        if self._does_event_exist(event_key):
            warn("Event already exists. event_key: {0}, event_type: {1}", event_key, self._event_type)
            return False

        try:
            self._gcal.connection.events().insert(
                calendarId=self._calendar_id, body=event_data
            ).execute()
            info("Created event. event_data: {0}", event_data)
            return True
        except HttpError as exc:
            self._handle_api_error(exc)
            return False

    @abstractmethod
    def _build_event(self, item: Model) -> dict[str, any]:
        """イベントデータを構築する。

        Args:
            item: イベントのモデル。

        Returns:
            dict[str, any]: Google Calendar API用のイベントデータ。
        """

    @abstractmethod
    def _get_event_key(self, item: Model) -> tuple:
        """イベントの一意キーを取得する。

        Args:
            item: イベントのモデル。

        Returns:
            tuple: イベントを一意に識別するキー。
        """

    @abstractmethod
    def _extract_event_key(self, event: dict, props: dict) -> tuple:
        """Google Calendarイベントから一意キーを抽出する。

        Args:
            event: Google Calendarイベントデータ。
            props: イベントの拡張プロパティ。

        Returns:
            tuple: イベントを一意に識別するキー。
        """

    def _does_event_exist(self, event_key: tuple) -> bool:
        """指定されたイベントがGoogle Calendarに存在するか確認する。

        Args:
            event_key: イベントを一意に識別するキー。

        Returns:
            bool: イベントが存在する場合はTrue、しない場合はFalse。

        Raises:
            GoogleCalendarError: APIエラーが発生した場合。
        """
        if not self._gcal:
            return False

        try:
            events = self._gcal.connection.events().list(
                calendarId=self._calendar_id,
                privateExtendedProperty=f"{EVENT_TYPE_KEY}={self._event_type}",
                maxResults=MAX_EVENT_RESULTS
            ).execute()
            for event in events.get("items", []):
                props = event.get("extendedProperties", {}).get("private", {})
                stored_key = self._extract_event_key(event, props)
                if stored_key == event_key:
                    return True
            return False
        except HttpError as exc:
            self._handle_api_error(exc)
            return False

    def _handle_api_error(self, exc: HttpError) -> None:
        """Google Calendar APIエラーを処理する。

        Args:
            exc: 発生したHTTPエラー。

        Raises:
            GoogleCalendarPermissionError: 権限エラー（403）の場合。
            GoogleCalendarRateLimitError: レート制限（429）の場合。
            GoogleCalendarError: その他のAPIエラーの場合。
        """
        try:
            status = exc.resp.status
            if status == 403:
                warn("Permission error for calendar. calendar_id: {0}", self._calendar_id)
                raise GoogleCalendarPermissionError(
                    f"Insufficient permissions for calendar {self._calendar_id}") from exc
            elif status == 429:
                warn("Rate limit exceeded for calendar. calendar_id: {0}", self._calendar_id)
                raise GoogleCalendarRateLimitError("Rate limit exceeded") from exc
            else:
                warn("Google Calendar API error. calendar_id: {0}, error: {1}", self._calendar_id, str(exc))
                raise GoogleCalendarError(f"API error: {exc}") from exc
        except AttributeError as attr_err:
            warn("Unexpected error for calendar. calendar_id: {0}, error: {1}", self._calendar_id, str(exc))
            raise GoogleCalendarError(f"Unexpected error: {exc}") from attr_err

    def _convert_to_google_datetime(self, dt: str | datetime | None) -> str | None:
        """日時をGoogle CalendarのRFC3339形式に変換する。

        Args:
            dt: 変換する日時（文字列またはdatetimeオブジェクト）。

        Returns:
            str | None: RFC3339形式の文字列（例: '2025-04-11T10:07:00+09:00'）。入力がNoneの場合はNone。

        Raises:
            ValueError: 日時フォーマットが無効な場合。
        """
        if dt is None:
            return None
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M")
            except ValueError as exc:
                warn(f"Invalid datetime format: {dt}, error={exc}")
                raise
        return dt.isoformat(timespec="seconds") + "+09:00"
