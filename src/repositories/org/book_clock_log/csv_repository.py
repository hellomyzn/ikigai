"""repository.org.book_clock_log.csv_repository"""
#########################################################
# Builtin packages
#########################################################
# (None)

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
from models.org import BookClockLog
from repositories import CsvBaseRepository, CsvConfig


class CsvBookClockLogRepository(CsvBaseRepository):
    """BookClockLogデータをCSVに保存するリポジトリ。

    CsvBaseを継承し、Book専用のCsvConfigを設定する。
    """

    def __init__(self):
        config = CsvConfig(
            file_name="BookClockLogs.csv",
            base_path="/opt/work/src/csv/org/book",
            columns=[
                "id", "book_id", "clock_start", "clock_end", "duration_min"
            ],
            key_map={
                "id": "id",
                "book_id": "book_id",
                "clock_start": "clock_start",
                "clock_end": "clock_end",
                "duration_min": "duration_min"
            },
            model_type=BookClockLog
        )
        super().__init__(config)
