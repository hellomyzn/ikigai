"""repositories/org/book_log/csv_repository.py"""
from repositories.csv_base import CsvBase
from repositories.model_adapter import ModelAdapter
from models.org import BookLog  # Bookモデル

class CsvBookLogRepository(CsvBase):
    """_summary_

    Args:
        CsvBase (_type_): _description_
    """
    FILE_NAME = "BookLogs.csv"
    PATH = "/opt/work/src/csv/org/book"

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
        adapter = ModelAdapter(model=BookLog, key_map=key_map)
        filepath = f"{self.PATH}/{self.FILE_NAME}"
        super().__init__(path=filepath, header=columns, adapter=adapter)
