import pytest
import csv
from unittest.mock import mock_open, patch, MagicMock
from repositories.org.book.csv_repository import CsvBookRepository
from models.org import Book

# CsvBookRepositoryのテスト


class TestCsvBookRepository:
    @pytest.fixture
    def book_repository(self):
        with patch("os.path.join", return_value="/opt/work/src/csv/org/book/Books.csv"):
            return CsvBookRepository()

    def test_initialization(self, book_repository):
        # 初期化が正しく行われるか
        assert book_repository._path == "/opt/work/src/csv/org/book/Books.csv"
        assert book_repository._header == [
            "id", "title", "effort", "created_at", "ended_at",
            "scheduled_at", "deadline_at", "url", "tags", "notes"
        ]
        assert book_repository._adapter.model == Book

    def test_add_book(self, book_repository):
        # Bookモデルを使った追加のテスト
        book = Book(
            id=1, title="Test Book", effort="1h", created_at="2023-01-01",
            ended_at="", scheduled_at="", deadline_at="2023-01-02",
            url="http://example.com", tags="tag1", notes="Note1"
        )
        mock_file = mock_open()
        with patch("builtins.open", mock_file), \
                patch.object(book_repository, "_has_header", return_value=True):
            book_repository.add([book])
            mock_file().write.assert_called()
            # 書き込み内容を確認
            expected_data = {
                "id": 1, "title": "Test Book", "effort": "1h",
                "created_at": "2023-01-01", "ended_at": "",
                "scheduled_at": "", "deadline_at": "2023-01-02",
                "url": "http://example.com", "tags": "tag1", "notes": "Note1"
            }
            # DictWriterのモックを作成して確認
            mock_writer = MagicMock()
            with patch("csv.DictWriter", return_value=mock_writer):
                book_repository.add([book])
                mock_writer.writerows.assert_called_with([expected_data])
