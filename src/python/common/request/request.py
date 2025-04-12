"""common.requests.requests"""
##################################################
# Python提供パッケージ
##################################################
from typing import Callable, Final
import requests

##################################################
# 外部ライブラリ提供パッケージ
##################################################
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

##################################################
# 開発パッケージ
##################################################
from common.log import error, warn
from common.retry import create_retry_decorator

DEF_ATTEMPTS: Final[int] = 3
DEF_WAIT_SEC: Final[int] = 10
DEF_TIMEOUT_SEC: Final[int] = 60


def get(url: str, params: dict = None, headers: dict = None,
        attempts: int = DEF_ATTEMPTS, wait_sec: int = DEF_WAIT_SEC,
        timeout: int = DEF_TIMEOUT_SEC, is_reraise: bool = False, **kwargs) -> requests.models.Response:
    """リトライ処理付きのrequests.getのwrapper

    Args:
        url (str): GETリクエストするURL
        params (dict): URLパラメータ
        headers (dict): リクエストヘッダ
        attempts (int): リトライ回数
        wait_sec (int): リトライ間隔(秒)
        timeout (int): タイムアウト(秒)
        is_reraise (bool): True: 発生した例外でraise / False: Retry Exceptionでraise

    Raises:
        RetryError: リトライエラー

    Returns:
        Response: requests.getのレスポンス
    """
    retry_decorator = create_retry_decorator(attempts=attempts, wait_sec=wait_sec, is_reraise=is_reraise)

    @retry_decorator
    def __get():
        """requests.get実行処理

        Raises:
            RequestException: リクエスト失敗時のエラー

        Returns:
            Response: requests.getのレスポンス
        """
        try:
            res = requests.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
            # status_code 4XX,5XX系はExceptionにする
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as exp:
            warn("Failed to send GET request. {0}", exp)
            raise exp
        except Exception as exp:
            warn("An unexpected error occurred. {0}", exp)
            raise exp

    try:
        return __get()
    except RetryError as exp:
        error("Failed to send GET request with retry. url: {0}, params: {1}, headers: {2}, "
              "attempts: {3}, wait_sec: {4}, timeout: {5}, kwargs: {6}",
              url, params, headers, attempts, wait_sec, timeout, kwargs)
        raise exp


def post(url: str, data: dict = None, json=None, headers: dict = None,
         attempts: int = DEF_ATTEMPTS, wait_sec: int = DEF_WAIT_SEC,
         timeout: int = DEF_TIMEOUT_SEC, is_reraise: bool = False, ** kwargs) -> requests.models.Response:
    """リトライ処理付きのrequests.postのwrapper

    Args:
        url (str): POSTリクエストするURL
        data (dict):  Bodyデータ
        json (optional): Jsonデータ
        headers (dict): リクエストヘッダ
        attempts (int): リトライ回数
        wait_sec (int): リトライ間隔(秒)
        timeout (int): タイムアウト(秒)
        is_reraise (bool): True: 発生した例外でraise / False: Retry Exceptionでraise

    Raises:
        RequestException: リクエスト失敗時のエラー
        RetryError: リトライエラー

    Returns:
        Response: requests.postのレスポンス
    """
    retry_decorator = create_retry_decorator(attempts=attempts, wait_sec=wait_sec, is_reraise=is_reraise)

    @retry_decorator
    def __post():
        """requests.post実行処理

        Raises:
            RequestException: リクエスト失敗時のエラー

        Returns:
            Response: requests.postのレスポンス
        """
        try:
            res = requests.post(url, data=data, json=json, headers=headers, timeout=timeout, **kwargs)
            # status_code 4XX,5XX系はExceptionにする
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as exp:
            warn("Failed to send POST request. {0}", exp)
            raise exp
        except Exception as exp:
            warn("An unexpected error occurred. {0}", exp)
            raise exp

    try:
        return __post()
    except RetryError as exp:
        error("Failed to send POST request with retry. url: {0}, data: {1}, json: {2}, "
              "headers: {3}, attempts: {4}, wait_sec: {5}, timeout: {6}, kwargs: {7}",
              url, data, json, headers, attempts, wait_sec, timeout, kwargs)
        raise exp


def patch(url: str, data: dict = None, json=None, headers: dict = None,
          attempts: int = DEF_ATTEMPTS, wait_sec: int = DEF_WAIT_SEC,
          timeout: int = DEF_TIMEOUT_SEC, is_reraise: bool = False, ** kwargs) -> requests.models.Response:
    """リトライ処理付きのrequests.patchのwrapper

    Args:
        url (str): PATCHリクエストするURL
        data (dict):  Bodyデータ
        json (optional): Jsonデータ
        headers (dict): リクエストヘッダ
        attempts (int): リトライ回数
        wait_sec (int): リトライ間隔(秒)
        timeout (int): タイムアウト(秒)
        is_reraise (bool): True: 発生した例外でraise / False: Retry Exceptionでraise

    Raises:
        RequestException: リクエスト失敗時のエラー
        RetryError: リトライエラー

    Returns:
        Response: requests.patchのレスポンス
    """
    retry_decorator = create_retry_decorator(attempts=attempts, wait_sec=wait_sec, is_reraise=is_reraise)

    @retry_decorator
    def __patch():
        """requests.patch実行処理

        Raises:
            RequestException: リクエスト失敗時のエラー

        Returns:
            Response: requests.patchのレスポンス
        """
        try:
            res = requests.patch(url, data=data, json=json, headers=headers, timeout=timeout, **kwargs)
            # status_code 4XX,5XX系はExceptionにする
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as exp:
            warn("Failed to send PATCH request. {0}", exp)
            raise exp
        except Exception as exp:
            warn("An unexpected error occurred. {0}", exp)
            raise exp

    try:
        return __patch()
    except RetryError as exp:
        error("Failed to send PATCH request with retry. url: {0}, data: {1}, json: {2}, "
              "headers: {3}, attempts: {4}, wait_sec: {5}, timeout: {6}, kwargs: {7}",
              url, data, json, headers, attempts, wait_sec, timeout, kwargs)
        raise exp


def put(url: str, data: dict = None, json=None, headers: dict = None,
        attempts: int = DEF_ATTEMPTS, wait_sec: int = DEF_WAIT_SEC,
        timeout: int = DEF_TIMEOUT_SEC, is_reraise: bool = False, **kwargs) -> requests.models.Response:
    """リトライ処理付きのrequests.putのwrapper

    Args:
        url (str): PUTリクエストするURL
        data (dict):  Bodyデータ
        json (optional): Jsonデータ
        headers (dict): リクエストヘッダ
        attempts (int): リトライ回数
        wait_sec (int): リトライ間隔(秒)
        timeout (int): タイムアウト(秒)
        is_reraise (bool): True: 発生した例外でraise / False: Retry Exceptionでraise

    Raises:
        RequestException: リクエスト失敗時のエラー
        RetryError: リトライエラー

    Returns:
        Response: requests.putのレスポンス
    """
    retry_decorator = create_retry_decorator(attempts=attempts, wait_sec=wait_sec, is_reraise=is_reraise)

    @retry_decorator
    def __put():
        """requests.put実行処理

        Raises:
            RequestException: リクエスト失敗時のエラー

        Returns:
            Response: requests.putのレスポンス
        """
        try:
            res = requests.put(url, data=data, json=json, headers=headers, timeout=timeout, **kwargs)
            # status_code 4XX,5XX系はExceptionにする
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as exp:
            warn("Failed to send PUT request. {0}", exp)
            raise exp
        except Exception as exp:
            warn("An unexpected error occurred. {0}", exp)
            raise exp

    try:
        return __put()
    except RetryError as exp:
        error("Failed to send PUT request with retry. url: {0}, data: {1}, json: {2}, "
              "headers: {3}, attempts: {4}, wait_sec: {5}, timeout: {6}, kwargs: {7}",
              url, data, json, headers, attempts, wait_sec, timeout, kwargs)
        raise exp


def head(url: str, params: dict = None, headers: dict = None,
         attempts: int = DEF_ATTEMPTS, wait_sec: int = DEF_WAIT_SEC,
         timeout: int = DEF_TIMEOUT_SEC, is_reraise: bool = False, **kwargs) -> requests.models.Response:
    """リトライ処理付きのrequests.headのwrapper

    Args:
        url (str): headリクエストするURL
        params (dict): URLパラメータ
        headers (dict): リクエストヘッダ
        attempts (int): リトライ回数
        wait_sec (int): リトライ間隔(秒)
        timeout (int): タイムアウト(秒)
        is_reraise (bool): True: 発生した例外でraise / False: Retry Exceptionでraise

    Raises:
        RetryError: リトライエラー

    Returns:
        Response: requests.headのレスポンス
    """
    retry_decorator = create_retry_decorator(attempts=attempts, wait_sec=wait_sec, is_reraise=is_reraise)

    @retry_decorator
    def __head():
        """requests.head実行処理

        Raises:
            RequestException: リクエスト失敗時のエラー

        Returns:
            Response: requests.headのレスポンス
        """
        try:
            res = requests.head(url, params=params, headers=headers, timeout=timeout, **kwargs)
            # status_code 4XX,5XX系はExceptionにする
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as exp:
            warn("Failed to send head request. {0}", exp)
            raise exp
        except Exception as exp:
            warn("An unexpected error occurred. {0}", exp)
            raise exp

    try:
        return __head()
    except RetryError as exp:
        error("Failed to send head request with retry. url: {0}, params: {1}, headers: {2}, "
              "attempts: {3}, wait_sec: {4}, timeout: {5}, kwargs: {6}",
              url, params, headers, attempts, wait_sec, timeout, kwargs)
        raise exp
