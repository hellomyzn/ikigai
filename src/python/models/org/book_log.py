from dataclasses import dataclass, field
import json

from models import Model

@dataclass
class BookLog(Model):
    """BookLog model"""
    id: int | None = field(init=True, default=None)
    book_id: int | None = field(init=True, default=None)
    state: str | None = field(init=True, default=None)
    from_status: str | None = field(init=True, default=None)
    timestamp: str | None = field(init=True, default=None)

    @classmethod
    def from_dict(cls, dict_: dict):
        """convert from dict to BookLog model"""
        return cls(**{
            "id": dict_.get("id"),
            "book_id": dict_.get("book_id"),
            "state": dict_.get("state"),
            "from_status": dict_.get("from_status"),
            "timestamp": dict_.get("timestamp")
        })

    def to_dict(self, without_none_field: bool = False) -> dict:
        """convert from model to dict"""
        dict_ = {
            "id": self.id,
            "book_id": self.book_id,
            "state": self.state,
            "from_status": self.from_status,
            "timestamp": self.timestamp
        }

        if without_none_field:
            return {key: value for key, value in dict_.items() if value is not None}

        return dict_

    def to_json(self) -> str:
        """convert from model to json"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
