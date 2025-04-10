"""common.decorator.decorator for gss"""
#########################################################
# Builtin packages
#########################################################
import functools
import time
import requests

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
from common.log import error, warn
from common.exceptions import (
    MyGssException,
    MyGssInvalidArgumentException,
    MyGssResourceExhaustedException
)


def __handle_error(exc: Exception) -> int:
    """例外に応じた待機秒数を返すハンドラ

    Args:
        exc (Exception): 発生した例外

    Returns:
        int: 次のリトライまでの待機秒数
    """
    if isinstance(exc, requests.exceptions.ConnectionError):
        warn("Connection error: {}: {}", exc.__class__.__name__, exc)
        return 30
    elif isinstance(exc, MyGssInvalidArgumentException):
        return 5
    elif isinstance(exc, MyGssResourceExhaustedException):
        return 60
    elif isinstance(exc, MyGssException):
        return 1
    else:
        return 1  # 他の例外については最低限の待機


def gss_module(func):
    """_summary_

    Args:
        func (_type_): _description_

    Raises:
        MyGssException: _description_

    Returns:
        _type_: _description_
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except MyGssException as exc:
                if attempt == max_attempts:
                    mes = f"Failed to connect to gss after {attempt} attempts. Please check your connection or logs."
                    error(mes)
                    raise MyGssException(mes) from exc
                wait_sec = __handle_error(exc)
                warn("Attempt {0} failed; waiting {1} sec", attempt, wait_sec)
                time.sleep(wait_sec)
    return wrapper
