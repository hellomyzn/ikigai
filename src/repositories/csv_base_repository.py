"""repositories.csv_base_repository"""
#########################################################
# Builtin packages
#########################################################
import csv
import os
from dataclasses import dataclass

#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
from common.log import error, warn, info
from models import Model
from repositories.base_repository import BaseRepositoryInterface
from repositories.model_adapter import ModelAdapter


@dataclass
class CsvConfig:
    """CSVリポジトリの設定クラス。

    Attributes:
        file_name: CSVファイル名。
        base_path: CSVファイルのベースパス。
        columns: CSVのカラムリスト。
        key_map: モデルとCSVカラムのマッピング。
        model_type: モデルクラス。
    """
    file_name: str
    base_path: str
    columns: list[str]
    key_map: dict
    model_type: type[Model]


class CsvBaseRepository(BaseRepositoryInterface):
    """CSVベースのリポジトリ基底クラス。

    Args:
        config: CSVリポジトリの設定。
    """

    def __init__(self, config: CsvConfig):
        self._path = os.path.join(config.base_path, config.file_name)
        self._header = config.columns
        self._adapter = ModelAdapter(model=config.model_type, key_map=config.key_map)

    def all(self) -> list[dict]:
        """CSVから全データを取得する。

        Returns:
            list[dict]: 全データレコードのリスト。ファイルが存在しない場合は空リスト。
        """
        if not os.path.isfile(self._path):
            self._write_header()
            return []
        if not self._has_header():
            self._write_header()

        with open(self._path, encoding="utf-8", mode="r") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def find_by_id(self, id_: int) -> dict | None:
        """指定されたIDのデータを取得する。

        Args:
            id_: 取得するデータのID。

        Returns:
            dict | None: 該当するデータ。見つからない場合はNone。
        """
        for data in self.all():
            try:
                if int(data.get("id", -1)) == int(id_):
                    return data
            except (KeyError, ValueError):
                continue
        return None

    def add(self, data: list[Model]) -> None:
        """データをCSVに追記する。

        Args:
            data: 追記するデータのリスト。
        """
        if not data:
            return

        inputs = [self._adapter.from_model(model) for model in data]
        if not self._has_header():
            self._write_header()

        with open(self._path, encoding="utf-8", mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self._header)
            writer.writerows(inputs)
        info("Added data to CSV file: {}", self._path)

    def delete_by_id(self, id_: int) -> None:
        """指定されたIDのデータを削除する（未実装）。

        Args:
            id_: 削除するデータのID。

        Raises:
            NotImplementedError: 常に発生（未実装）。
        """
        warn("Not implemented")
        return

    def find_next_id(self) -> int:
        """次に使用可能なIDを取得する。

        Returns:
            int: 次に使用するID。データが存在しない場合は1。
        """
        records = self.all()
        if not records:
            return 1
        try:
            max_id = max(int(record["id"]) for record in records if record.get("id"))
            return max_id + 1
        except (ValueError, KeyError):
            return 1

    def _has_header(self) -> bool:
        """CSVファイルに正しいヘッダーが存在するか確認する。

        Returns:
            bool: ヘッダーが存在し、期待されるカラムと一致する場合はTrue。
        """
        if not os.path.isfile(self._path):
            return False
        with open(self._path, encoding="utf-8", mode="r") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames
            if header is None:
                warn("Header is None in CSV file: {}", self._path)
                return False
            if set(header) != set(self._header):
                error("Invalid header in CSV file: {}. Found: {}, Expected: {}",
                      self._path, header, self._header)
                return False
        return True

    def _write_header(self) -> None:
        """CSVファイルにヘッダーを書き込む。"""
        with open(self._path, encoding="utf-8", mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self._header)
            writer.writeheader()
        info("Wrote header to CSV file: {}. Header: {}", self._path, self._header)
