"""common.google_spreadsheet.gss_accessor"""
#########################################################
# Builtin packages
#########################################################

#########################################################
# 3rd party packages
#########################################################
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#########################################################
# Own packages
#########################################################
from utils import Singleton
from common.config import Config
from common.log import (
    info,
    error_stack_trace
)


class GssAccessor(Singleton):
    """
        Usage:
            1. put json file of your API key in src/src/json.
            2. put config below in src/common/config/config.ini
                - JSON_PATH
                - SHEET_KEY
                - SHEET_NAME
            e.g.
                from common.google_spreadsheet import GssAccessor
                gss = GssAccessor()
                workbook = gss.connection.open_by_key(sheet_key)
                worksheet = workbook.worksheet(sheet_name)
                first_column_data = list(filter(None, worksheet.col_values(1)))

        Reference:
        - https://qiita.com/164kondo/items/eec4d1d8fd7648217935
        - https://www.cdatablog.jp/entry/2019/04/16/191006
    """
    # Shared connection
    __connection = None

    def __init__(self):
        self.__connection = self.__initialize()

    @property
    def connection(self) -> gspread.client.Client:
        """Getter for __connection

        Returns:
            self.__connection (ConfigParser): Private property __connection
        """
        return self.__connection

    def __initialize(self) -> gspread.client.Client:
        """Connect Google Spreadsheet

        Returns:
            connection: connection for google_spreadsheet
        """
        if self.__connection is not None:
            return self.__connection

        connection = None
        config = Config().config
        json_path = config['GSS']['JSON_PATH']
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        info('Start connecting Google Spreadsheet')

        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
            connection = gspread.authorize(credentials)
            info('Succeed in connecting Google Spreadsheet')

        except Exception as err:
            error_stack_trace(
                f"Fail to connect Google Spreadsheet. error: {err}, json_path: {json_path}, scope: {scope}")

        return connection
