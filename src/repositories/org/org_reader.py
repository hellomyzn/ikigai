"""repositories.org.org_reader"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import orgparse
from orgparse.node import OrgNode
from orgparse.date import OrgDate

class OrgReader:
    """OrgファイルからBook, BookLog, BookClockLogデータを抽出するReader"""

    DATE_FORMAT = "%Y-%m-%d %H:%M"
    BOOK_TAG = "book"
    EXCLUDED_HEADINGS = {"URL", "Notes"}
    CREATED_AT_PREFIX = "CREATED_AT:"

    def __init__(self, org_file_paths: List[str]):
        self.org_file_paths = org_file_paths

    def load_books(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Book, BookLog, BookClockLogデータをまとめて取得する"""
        books = []
        book_logs = []
        book_clock_logs = []

        for path in self.org_file_paths:
            try:
                root = orgparse.load(path)
                for node in root[1:]:
                    if not self._is_valid_book_node(node):
                        continue

                    # Bookデータ
                    book = self._parse_book_node(node)
                    books.append(book)

                    # BookLogデータ
                    book_logs.extend(self._parse_book_logs(node, book))

                    # BookClockLogデータ
                    book_clock_logs.extend(self._parse_book_clock_logs(node, book))

            except FileNotFoundError:
                print(f"Warning: Org file not found: {path}")
                continue

        return books, book_logs, book_clock_logs

    def _is_valid_book_node(self, node: OrgNode) -> bool:
        """ノードが本のデータとして有効か判定する"""
        return (
            self.BOOK_TAG in (node.tags or set())
            and node.heading.strip() not in self.EXCLUDED_HEADINGS
        )

    def _parse_book_node(self, node: OrgNode) -> Dict:
        """Bookデータを辞書形式で作成する"""
        return {
            "title": node.heading.strip(),
            "effort": self._extract_property(node, "Effort"),
            "created_at": self._extract_created_at(node),
            "ended_at": self._format_datetime(node.closed.start),
            "scheduled_at": self._format_datetime(node.scheduled.start),
            "deadline_at": self._format_datetime(node.deadline.start),
            "url": self._extract_child_body(node, "URL"),
            "tags": ":".join(node.tags) if node.tags else None,
            "notes": self._extract_child_body(node, "Notes"),
        }

    def _parse_book_logs(self, node: OrgNode, book: Dict) -> List[Dict]:
        """LOGBOOKから状態遷移ログを抽出する"""
        logs = []
        for task in node.repeated_tasks:
            if not (task.before and task.after):
                continue
            timestamp = None
            if task.start:
                timestamp = (
                    task.start.strftime(self.DATE_FORMAT)
                    if task.has_time
                    else task.start.strftime("%Y-%m-%d 00:00")
                )
            logs.append({
                "state": task.after,
                "from_status": task.before,
                "timestamp": timestamp,
                "book": book,  # Book情報を保持（book_idを後で解決）
            })
        return logs

    def _parse_book_clock_logs(self, node: OrgNode, book: Dict) -> List[Dict]:
        """LOGBOOKから作業時間ログを抽出する"""
        clocks = []
        for clock in node.clock:
            duration_min = (
                int(clock.duration.total_seconds() / 60)
                if clock.duration
                else None
            )
            clocks.append({
                "clock_start": self._format_datetime(clock.start),
                "clock_end": self._format_datetime(clock.end),
                "duration_min": duration_min,
                "book": book,  # Book情報を保持（book_idを後で解決）
            })
        return clocks

    def _extract_property(self, node: OrgNode, prop: str) -> Optional[str]:
        """指定されたプロパティを抽出する"""
        return node.get_property(prop)

    def _extract_created_at(self, node: OrgNode) -> Optional[str]:
        """CREATED_ATフィールドを抽出する"""
        if not node.body:
            return None
        for line in node.body.splitlines():
            line = line.strip()
            if line.startswith(self.CREATED_AT_PREFIX):
                return line[len(self.CREATED_AT_PREFIX):].strip()
        return None

    def _extract_child_body(self, node: OrgNode, title: str) -> Optional[str]:
        """子ノードのボディを抽出する（URLやNotes）"""
        for child in node.children:
            if child.heading.strip() == title:
                return child.body.strip() if child.body else None
        return None

    def _format_datetime(self, org_date: str) -> Optional[str]:
        """OrgDateオブジェクトをフォーマットされた文字列に変換する"""
        return org_date.strftime(self.DATE_FORMAT) if org_date else None