from repositories.gss_base import GSSBase
from repositories.model_adapter import ModelAdapter
from models.org import Book
from common.config import Config

CONFIG = Config().config
SHEET_KEY = CONFIG["GSS"]["ORG_BOOK_SHEET_KEY"]


class GssBookRepository(GSSBase):

    def __init__(self):
        columns = [
            "id", "title", "effort",
            "created_at", "ended_at", "scheduled_at", 
            "deadline_at", "url", "tags", "notes"
        ]
        key_map = {
            "id": "id",
            "title": "title",
            "effort": "effort",
            "created_at": "created_at",
            "ended_at": "ended_at",
            "scheduled_at": "scheduled_at",
            "deadline_at": "deadline_at",
            "url": "url",
            "tags": "tags",
            "notes": "notes"
        }
        self.sheet_key = SHEET_KEY
        self.sheet_name = "Books"
        self.sheet_log_name = "BookLogs"
        self.sheet_clock_log_name = "BookClockLogs"
        adapter = ModelAdapter(model=Book, key_map=key_map)
        super().__init__(sheet_key=self.sheet_key, sheet_name=self.sheet_name, columns=columns, adapter=adapter)

    def all(self) -> list[Book]:
        # 仮データを返す
        return [
            Book(id=1, title="ゆるストイック", priority="B", effort=3.0, created_at="2025-04-10 10:00", ended_at=None, scheduled_at=None, deadline_at=None, tags=":book:", notes="メモ1"),
            Book(id=2, title="オブジェクト指向設計", priority="A", effort=5.0, created_at="2025-04-10 11:00", ended_at=None, scheduled_at=None, deadline_at=None, tags=":book:study:", notes="メモ2"),
            Book(id=3, title="自己管理大全", priority="C", effort=2.0, created_at="2025-04-10 12:00", ended_at=None, scheduled_at=None, deadline_at=None, tags=":book:", notes="メモ3"),
        ]