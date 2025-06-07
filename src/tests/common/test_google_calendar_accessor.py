import pytest
from common.google_calendar.google_calendar_accessor import GoogleCalendarAccessor
from common.exceptions import GoogleCalendarError

class DummyConfig:
    def __init__(self):
        self.config = {
            "GSS": {"JSON_PATH": "dummy.json"},
            "CALENDAR": {"CALENDAR_ID": "dummy"},
        }

def test_initialize_raises_google_calendar_error(monkeypatch):
    monkeypatch.setattr(
        "common.google_calendar.google_calendar_accessor.Config",
        lambda: DummyConfig()
    )
    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("not found")
    monkeypatch.setattr(
        "common.google_calendar.google_calendar_accessor.service_account.Credentials.from_service_account_file",
        raise_file_not_found,
    )
    if hasattr(GoogleCalendarAccessor, "_instance"):
        delattr(GoogleCalendarAccessor, "_instance")
    GoogleCalendarAccessor._GoogleCalendarAccessor__connection = None
    with pytest.raises(GoogleCalendarError):
        GoogleCalendarAccessor()
