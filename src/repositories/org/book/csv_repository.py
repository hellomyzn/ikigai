from repositories.csv_base import CsvBase
from repositories.model_adapter import ModelAdapter
from models.org import Book  # Bookモデル

class CsvBookRepository(CsvBase):
    FILE_NAME = "Books.csv"
    PATH = "/opt/work/src/csv/org/book"

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
        adapter = ModelAdapter(model=Book, key_map=key_map)
        filepath = f"{self.PATH}/{self.FILE_NAME}"
        super().__init__(path=filepath, header=columns, adapter=adapter)
