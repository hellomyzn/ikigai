from repositories.gss_base import GSSBase
from repositories.model_adapter import ModelAdapter
from models.org import BookLog
from common.config import Config

CONFIG = Config().config
SHEET_KEY = CONFIG["GSS"]["ORG_BOOK_SHEET_KEY"]


class GssBookLogRepository(GSSBase):
    """Repository for BookLog"""

    def __init__(self):
        columns = [
            "id", "book_id", "state", "from_status", "timestamp"
        ]
        key_map = {
            "id": "id",
            "book_id": "book_id",
            "state": "state",
            "from_status": "from_status",
            "timestamp": "timestamp"
        }
        self.sheet_key = SHEET_KEY
        self.sheet_name = "BookLogs"

        adapter = ModelAdapter(model=BookLog, key_map=key_map)
        super().__init__(sheet_key=self.sheet_key, sheet_name=self.sheet_name, columns=columns, adapter=adapter)

    def all(self) -> list[BookLog]:
        # 仮データを返す
        return [
            BookLog(id=1, book_id=1, state="DONE", from_status="TODO", timestamp="2025-04-10 15:00"),
            BookLog(id=2, book_id=2, state="DONE", from_status="TODO", timestamp="2025-04-10 16:00"),
            BookLog(id=3, book_id=3, state="DONE", from_status="TODO", timestamp="2025-04-10 17:00"),
        ]
