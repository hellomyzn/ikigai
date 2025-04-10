from repositories.csv_base import CsvBase
from repositories.model_adapter import ModelAdapter
from models.org import Book  # Bookモデル

class CsvBookRepository(CsvBase):
    FILE_NAME = "Books.csv"

    def __init__(self):
        columns = [
            "id", "title", "priority", "effort",
            "created_at", "ended_at", "scheduled_at", "deadline_at", "tags", "notes"
        ]
        key_map = {
            "id": "id",
            "title": "title",
            "priority": "priority",
            "effort": "effort",
            "created_at": "created_at",
            "ended_at": "ended_at",
            "scheduled_at": "scheduled_at",
            "deadline_at": "deadline_at",
            "tags": "tags",
            "notes": "notes"
        }
        adapter = ModelAdapter(model=Book, key_map=key_map)
        super().__init__(path=self.FILE_NAME, header=columns, adapter=adapter)
