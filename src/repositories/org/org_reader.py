"""repositories.org.org_reader"""
from orgparse import load

class OrgReader:
    """Orgファイルを読み取るReader"""

    def __init__(self, org_file_paths: list[str]):
        self.org_file_paths = org_file_paths

    def load_books(self) -> tuple[list[dict], list[dict], list[dict]]:
        """Book, BookLog, BookClockLog をまとめて取得する"""
        books = []
        book_logs = []
        book_clock_logs = []
        id_ = 1

        for path in self.org_file_paths:
            root = load(path)
            for node in root[1:]:
                if not self.__is_valid_book_node(node):
                    continue

                # Bookデータ
                books.append(self.__parse_book_node(node, id_))

                # BookLogデータ
                book_logs.extend(self.__parse_book_logs(node, id_))

                # BookClockLogデータ
                book_clock_logs.extend(self.__parse_book_clock_logs(node, id_))

                id_ += 1
        return books, book_logs, book_clock_logs

    @classmethod
    def __is_valid_book_node(cls, node) -> bool:
        """本のデータとみなせるノードかを判定"""
        if not node.tags or "book" not in node.tags:
            return False
        if node.heading.strip() in ("URL", "Notes"):
            return False
        return True

    @classmethod
    def __parse_book_node(cls, node, book_id: int) -> dict:
        """本(Book)データを作る"""
        return {
            "id": book_id,
            "title": node.heading.strip(),
            "effort": cls.__extract_property(node, "Effort"),
            "created_at": cls.__extract_created_at(node),
            "ended_at": cls.__extract_ended_at(node),
            "scheduled_at": cls.__extract_scheduled_at(node),
            "deadline_at": cls.__extract_deadline_at(node),
            "url": cls.__extract_child_body(node, "URL"),
            "tags": ":".join(node.tags) if node.tags else None,
            "notes": cls.__extract_child_body(node, "Notes"),
        }

    @classmethod
    def __parse_book_logs(cls, node, book_id: int) -> list[dict]:
        """LOGBOOKから状態遷移ログを作る"""
        logs = []
        repeated_tasks = getattr(node, "repeated_tasks", [])
        for log in repeated_tasks:
            logs.append({
                "id": None,
                "book_id": book_id,
                "state": log.after,
                "from_status": log.before,
                "timestamp": log.start.strftime("%Y-%m-%d %H:%M") if log.start else None,
            })
        return logs

    @classmethod
    def __parse_book_clock_logs(cls, node, book_id: int) -> list[dict]:
        """LOGBOOKから作業時間ログを作る"""
        clocks = []
        clock_entries = getattr(node, "clock", [])
        for clock in clock_entries:
            duration_min = int(clock.duration.total_seconds() / 60) if clock.duration else None
            clocks.append({
                "id": None,
                "book_id": book_id,
                "clock_start": clock.start.strftime("%Y-%m-%d %H:%M") if clock.start else None,
                "clock_end": clock.end.strftime("%Y-%m-%d %H:%M") if clock.end else None,
                "duration_min": duration_min,
            })
        return clocks

    @classmethod
    def __extract_property(cls, node, prop: str) -> str | None:
        """プロパティ値を抽出"""
        return node.get_property(prop)

    @classmethod
    def __extract_created_at(cls, node) -> str | None:
        """bodyからCREATED_ATを抽出"""
        if not node.body:
            return None
        for line in node.body.splitlines():
            if line.strip().startswith("CREATED_AT:"):
                return line.split("CREATED_AT:")[1].strip()
        return None

    @classmethod
    def __extract_scheduled_at(cls, node) -> str | None:
        """予定日"""
        return node.scheduled.start.strftime("%Y-%m-%d %H:%M") if node.scheduled else None

    @classmethod
    def __extract_deadline_at(cls, node) -> str | None:
        """締切日"""
        return node.deadline.start.strftime("%Y-%m-%d %H:%M") if node.deadline else None

    @classmethod
    def __extract_ended_at(cls, node) -> str | None:
        """完了日"""
        return node.closed.start.strftime("%Y-%m-%d %H:%M") if node.closed else None

    @classmethod
    def __extract_child_body(cls, node, title: str) -> str | None:
        """子ノードから本文を取り出す（URLやNotes）"""
        for child in node.children:
            if child.heading.strip() == title and child.body:
                return child.body.strip()
        return None
