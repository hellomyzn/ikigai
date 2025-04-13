"""repositories.csv_base"""
import csv
import os
from typing import List, Optional
from dataclasses import dataclass, field

from common.log import error, warn, info
from models import Model
from repositories import BaseRepositoryInterface
from repositories import ModelAdapter

@dataclass
class CsvBase(BaseRepositoryInterface):
    """CSVベースのリポジトリ"""

    path: str = field(init=True, default=None)
    header: List[str] = field(init=True, default_factory=list)
    adapter: ModelAdapter = field(init=True, default=None)

    def all(self) -> List[dict]:
        """CSVから全データを取得"""
        if not os.path.isfile(self.path):
            self._write_header()
            return []
        if not self._has_header():
            self._write_header()

        with open(self.path, encoding="utf-8", mode="r") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def find_by_id(self, id_: int) -> Optional[dict]:
        """IDでデータを検索"""
        for data in self.all():
            try:
                if int(data.get("id", -1)) == int(id_):
                    return data
            except (KeyError, ValueError):
                continue
        return None

    def write(self, data: List[Model], path: Optional[str] = None) -> None:
        """データをCSVに書き込む（上書き）"""
        target_path = path if path is not None else self.path
        with open(target_path, mode="w", encoding="utf-8", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.header)
            writer.writeheader()
            for model in data:
                dict_ = self.adapter.from_model(model)
                writer.writerow(dict_)
        info("Wrote data to CSV file: {}", target_path)

    def add(self, data: List[Model]) -> None:
        """データをCSVに追記"""
        if not data:
            return

        inputs = [self.adapter.from_model(model) for model in data]
        if not self._has_header():
            self._write_header()

        with open(self.path, encoding="utf-8", mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.header)
            writer.writerows(inputs)
        info("Added data to CSV file: {}", self.path)

    def delete_by_id(self, id_: int) -> None:
        """IDでデータを削除（未実装）"""
        pass

    def find_next_id(self) -> int:
        """次に使うべきIDを取得"""
        records = self.all()
        if not records:
            return 1
        try:
            max_id = max(int(record["id"]) for record in records if record.get("id"))
            return max_id + 1
        except (ValueError, KeyError):
            return 1

    def _has_header(self) -> bool:
        """CSVにヘッダーが存在するか確認"""
        if not os.path.isfile(self.path):
            return False
        with open(self.path, encoding="utf-8", mode="r") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            if header is None:
                warn("Header is None in CSV file: {}", self.path)
                return False
            if set(header) != set(self.header):
                error("Invalid header in CSV file: {}. Found: {}, Expected: {}",
                      self.path, header, self.header)
                return False
        return True

    def _write_header(self) -> None:
        """ヘッダーを書き込む"""
        with open(self.path, encoding="utf-8", mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.header)
            writer.writeheader()
        info("Wrote header to CSV file: {}. Header: {}", self.path, self.header)