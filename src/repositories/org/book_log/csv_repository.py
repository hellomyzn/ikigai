"""repositories.org.book_log.csv_repository.py"""
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
from models.org import BookLog
from repositories import CsvBaseRepository, CsvConfig


class CsvBookLogRepository(CsvBaseRepository):
    """BookLogデータをCSVに保存するリポジトリ。

    CsvBaseを継承し、Book専用のCsvConfigを設定する。
    """

    def __init__(self):
        config = CsvConfig(
            file_name="BookLogs.csv",
            base_path="/opt/work/src/csv/org/book",
            columns=[
                "id", "book_id", "state", "from_status", "timestamp"
            ],
            key_map={
                "id": "id",
                "book_id": "book_id",
                "state": "state",
                "from_status": "from_status",
                "timestamp": "timestamp"
            },
            model_type=BookLog
        )
        super().__init__(config)
