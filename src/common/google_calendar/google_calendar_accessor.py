"""common.google_calendar.google_calendar_accessor"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils import Singleton
from common.config import Config
from common.log import info, error_stack_trace

class GoogleCalendarAccessor(Singleton):
    """
    Google Calendar APIへの接続を提供するシングルトンクラス。

    Usage:
        from common.google_calendar import GoogleCalendarAccessor
        gcal = GoogleCalendarAccessor()
        service = gcal.connection
        events = service.events().list(calendarId='primary').execute()

    Config:
        - JSON_PATH: サービスアカウントの認証情報（credentials.json）
        - CALENDAR_ID: 対象カレンダーのID（例: 'primary'）

    Reference:
        - https://developers.google.com/calendar/api/guides/overview
    """
    __connection = None

    def __init__(self):
        self.__connection = self.__initialize()

    @property
    def connection(self):
        """接続オブジェクトのゲッター"""
        return self.__connection

    def __initialize(self):
        """Google Calendar APIへの接続を初期化"""
        if self.__connection is not None:
            return self.__connection

        config = Config().config
        json_path = config['GSS']['JSON_PATH']  # GSSと共有
        calendar_id = config['CALENDAR']['CALENDAR_ID']
        scopes = ['https://www.googleapis.com/auth/calendar']

        info('Start connecting Google Calendar')

        try:
            credentials = service_account.Credentials.from_service_account_file(
                json_path, scopes=scopes
            )
            connection = build('calendar', 'v3', credentials=credentials)
            # 接続テスト
            connection.events().list(calendarId=calendar_id, maxResults=1).execute()
            info('Succeed in connecting Google Calendar')
            return connection
        except (FileNotFoundError, HttpError) as err:
            error_stack_trace(
                f"Fail to connect Google Calendar. error: {err}, json_path: {json_path}, scopes: {scopes}"
            )
            raise