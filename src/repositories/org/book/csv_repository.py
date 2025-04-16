"""repository.org.book.csv_repository"""
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
from models.org import Book
from repositories import CsvBaseRepository, CsvConfig


class CsvBookRepository(CsvBaseRepository):
    """BookデータをCSVに保存するリポジトリ。

    CsvBaseを継承し、Book専用のCsvConfigを設定する。
    """

    def __init__(self):
        config = CsvConfig(
            file_name="Books.csv",
            base_path="/opt/work/src/csv/org/book",
            columns=[
                "id", "title", "effort",
                "created_at", "ended_at", "scheduled_at",
                "deadline_at", "url", "tags", "notes"
            ],
            key_map={
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
            },
            model_type=Book
        )
        super().__init__(config)
