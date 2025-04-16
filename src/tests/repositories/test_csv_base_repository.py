import pytest
import csv
import os
from unittest.mock import mock_open, patch, MagicMock
from dataclasses import dataclass
from repositories.csv_base_repository import CsvBaseRepository, CsvConfig

# テスト用のダミーモデル


@dataclass
class DummyModel:
    id: int
    title: str
    effort: str
    created_at: str
    ended_at: str
    scheduled_at: str
    deadline_at: str
    url: str
    tags: str
    notes: str

    def to_dict(self):
        """ModelAdapterが期待するto_dictメソッド"""
        return {
            "id": self.id,
            "title": self.title,
            "effort": self.effort,
            "created_at": self.created_at,
            "ended_at": self.ended_at,
            "scheduled_at": self.scheduled_at,
            "deadline_at": self.deadline_at,
            "url": self.url,
            "tags": self.tags,
            "notes": self.notes
        }

# テスト用のCsvConfig


@pytest.fixture
def csv_config(tmp_path):
    return CsvConfig(
        file_name="test.csv",
        base_path=str(tmp_path),
        columns=[
            "id", "title", "effort", "created_at", "ended_at",
            "scheduled_at", "deadline_at", "url", "tags", "notes"
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
        model_type=DummyModel
    )

# CsvBaseRepositoryのテスト


class TestCsvBaseRepository:
    @pytest.fixture
    def repository(self, csv_config):
        return CsvBaseRepository(csv_config)

    def test_all_file_not_exists(self, repository, tmp_path):
        # ファイルが存在しない場合、空リストを返す
        with patch("os.path.isfile", return_value=False):
            result = repository.all()
            assert result == []
            # ヘッダー書き込みが呼ばれることを確認
            with patch.object(repository, "_write_header") as mock_write:
                repository.all()
                mock_write.assert_called_once()

    def test_all_valid_file(self, repository, tmp_path):
        # 有効なCSVファイルが存在する場合
        csv_content = (
            "id,title,effort,created_at,ended_at,scheduled_at,deadline_at,url,tags,notes\n"
            "1,Test Book,1h,2023-01-01,,,2023-01-02,http://example.com,tag1,Note1\n"
        )
        m = mock_open(read_data=csv_content)
        with patch("builtins.open", m), patch("os.path.isfile", return_value=True):
            result = repository.all()
            assert len(result) == 1
            assert result[0]["id"] == "1"
            assert result[0]["title"] == "Test Book"

    def test_find_by_id_found(self, repository):
        # IDが見つかる場合
        csv_content = (
            "id,title,effort,created_at,ended_at,scheduled_at,deadline_at,url,tags,notes\n"
            "1,Test Book,1h,2023-01-01,,,2023-01-02,http://example.com,tag1,Note1\n"
        )
        with patch("builtins.open", mock_open(read_data=csv_content)), \
                patch("os.path.isfile", return_value=True):
            result = repository.find_by_id(1)
            assert result is not None
            assert result["id"] == "1"
            assert result["title"] == "Test Book"

    def test_find_by_id_not_found(self, repository):
        # IDが見つからない場合
        csv_content = (
            "id,title,effort,created_at,ended_at,scheduled_at,deadline_at,url,tags,notes\n"
            "1,Test Book,1h,2023-01-01,,,2023-01-02,http://example.com,tag1,Note1\n"
        )
        with patch("builtins.open", mock_open(read_data=csv_content)), \
                patch("os.path.isfile", return_value=True):
            result = repository.find_by_id(2)
            assert result is None

    def test_add_data(self, repository):
        # データ追加のテスト
        model = DummyModel(
            id=1, title="Test Book", effort="1h", created_at="2023-01-01",
            ended_at="", scheduled_at="", deadline_at="2023-01-02",
            url="http://example.com", tags="tag1", notes="Note1"
        )
        mock_file = mock_open()
        with patch("builtins.open", mock_file), \
                patch.object(repository, "_has_header", return_value=True):
            repository.add([model])
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
                repository.add([model])
                mock_writer.writerows.assert_called_with([expected_data])

    def test_find_next_id_no_records(self, repository):
        # レコードがない場合、ID=1を返す
        with patch.object(repository, "all", return_value=[]):
            result = repository.find_next_id()
            assert result == 1

    def test_find_next_id_with_records(self, repository):
        # レコードがある場合、最大ID+1を返す
        records = [{"id": "1"}, {"id": "3"}, {"id": "2"}]
        with patch.object(repository, "all", return_value=records):
            result = repository.find_next_id()
            assert result == 4

    def test_has_header_valid(self, repository):
        # 正しいヘッダーが存在する場合
        csv_content = (
            "id,title,effort,created_at,ended_at,scheduled_at,deadline_at,url,tags,notes\n"
        )
        with patch("builtins.open", mock_open(read_data=csv_content)), \
                patch("os.path.isfile", return_value=True):
            result = repository._has_header()
            assert result is True

    def test_has_header_invalid(self, repository):
        # ヘッダーが異なる場合
        csv_content = "id,title,invalid_column\n"
        with patch("builtins.open", mock_open(read_data=csv_content)), \
                patch("os.path.isfile", return_value=True):
            result = repository._has_header()
            assert result is False

    def test_write_header(self, repository):
        # ヘッダー書き込みのテスト
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            repository._write_header()
            mock_file().write.assert_called()
            # DictWriter.writeheaderが呼ばれたことを確認
            mock_writer = MagicMock()
            with patch("csv.DictWriter", return_value=mock_writer):
                repository._write_header()
                mock_writer.writeheader.assert_called_once()
