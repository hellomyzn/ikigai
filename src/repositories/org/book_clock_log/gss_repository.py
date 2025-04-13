from repositories.gss_base import GSSBase
from repositories.model_adapter import ModelAdapter
from models.org import BookClockLog
from common.config import Config

CONFIG = Config().config
SHEET_KEY = CONFIG["GSS"]["ORG_BOOK_SHEET_KEY"]


class GssBookClockLogRepository(GSSBase):
    """Repository for BookClockLog"""

    def __init__(self):
        columns = [
            "id", "book_id", "clock_start", "clock_end", "duration_min"
        ]
        key_map = {
            "id": "id",
            "book_id": "book_id",
            "clock_start": "clock_start",
            "clock_end": "clock_end",
            "duration_min": "duration_min"
        }
        self.sheet_key = SHEET_KEY
        self.sheet_name = "BookClockLogs"

        adapter = ModelAdapter(model=BookClockLog, key_map=key_map)
        super().__init__(sheet_key=self.sheet_key, sheet_name=self.sheet_name, columns=columns, adapter=adapter)

    def all(self) -> list[BookClockLog]:
        # 仮データを返す
        return [
            BookClockLog(id=1, book_id=1, clock_start="2025-04-10 10:00", clock_end="2025-04-10 10:30", duration=30),
            BookClockLog(id=2, book_id=2, clock_start="2025-04-10 11:00", clock_end="2025-04-10 11:30", duration=30),
            BookClockLog(id=3, book_id=3, clock_start="2025-04-10 12:00", clock_end="2025-04-10 12:30", duration=30),
        ]
