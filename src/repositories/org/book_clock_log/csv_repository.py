from repositories.csv_base import CsvBase
from repositories.model_adapter import ModelAdapter
from models.org import BookClockLog  # Bookモデル

class CsvBookClockLogRepository(CsvBase):
    """_summary_

    Args:
        CsvBase (_type_): _description_
    """
    FILE_NAME = "BookClockLogs.csv"
    PATH = "/opt/work/src/csv/org/book"

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
        adapter = ModelAdapter(model=BookClockLog, key_map=key_map)
        filepath = f"{self.PATH}/{self.FILE_NAME}"
        super().__init__(path=filepath, header=columns, adapter=adapter)
