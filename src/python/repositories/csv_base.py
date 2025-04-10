"""repositories.csv_base"""
#########################################################
# Builtin packages
#########################################################
import csv
import os
import sys
from dataclasses import dataclass, field


#########################################################
# 3rd party packages
#########################################################
# (None)

#########################################################
# Own packages
#########################################################
from common.log import error, warn, info
from models import Model
from repositories import BaseRepositoryInterface
from repositories import ModelAdapter


@dataclass
class CsvBase(BaseRepositoryInterface):
    """csv base repository"""

    path: str = field(init=True, default=None)
    header: list = field(init=True, default_factory=list)
    adapter: ModelAdapter = field(init=True, default=None)

    def all(self) -> list[dict,]:
        """get all data from csv

        Returns:
            list: all data from csv
        """
        if not os.path.isfile(self.path):
            # ファイルが存在しない場合はヘッダーを書き込み、空リストを返す
            self.__write_header()
            return []
        if not self.__has_header():
            self.__write_header()

        with open(self.path, encoding="utf-8", mode="r") as f:
            reader = csv.DictReader(f)
            all_data = [row for row in reader]
        return all_data

    def find_by_id(self, id_: int) -> dict:
        for data in self.all():
            try:
                if int(data.get("id", -1)) == int(id_):
                    return data
            except (KeyError, ValueError):
                continue
        return None

    def write(self, data: list[Model,], path: str | None = None) -> None:
        """データ（Modelオブジェクトのリスト）をCSVファイルへ書き込む"""

        target_path = path if path is not None else self.path

        with open(file=target_path, mode="w", encoding="utf-8", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.header)
            writer.writeheader()
            for model in data:
                dict_ = self.adapter.from_model(model)
                writer.writerow(dict_)
        info("Wrote data to CSV file: {}", target_path)

    def add(self, data: dict) -> None:
        """add data into the csv file
        1件分のレコードをCSVファイルへ追記する


        Args:
            data (dict): data to add
        """
        if not self.__has_header():
            self.__write_header()

        with open(self.path, encoding="utf-8", mode="a") as f:
            writer = csv.DictWriter(f, fieldnames=self.header)
            writer.writerow(data)

        info("added data in the csv file({0}).", self.path)

    def delete_by_id(self, id_: int) -> None:
        pass

    def __has_header(self) -> bool:
        """check the csv file has header or not

        Returns:
            bool: the csv file has header or not
        """
        with open(self.path, encoding="utf-8", mode="r") as f:
            reader = csv.DictReader(f)

            header = reader.fieldnames
            if header is None:
                warn("header is None in the csv file({0}).", self.path)

            if header != self.header:
                error("Invalid header in CSV file: {}. Found: {}, Expected: {}",
                      self.path, header, self.header)
                sys.exit(1)

        return bool(header)

    def __write_header(self) -> None:
        """write header
        """
        with open(self.path, encoding="utf-8", mode="w") as file:
            writer_ = csv.DictWriter(file, fieldnames=self.header)
            writer_.writeheader()
        info(f"write header in the csv file({0}). header: {1}",
             self.path, self.header)
