from dataclasses import dataclass, field
import json

from models import Model

@dataclass
class BookClockLog(Model):
    """BookClockLog model"""
    id: int | None = field(init=True, default=None)
    book_id: int | None = field(init=True, default=None)
    clock_start: str | None = field(init=True, default=None)
    clock_end: str | None = field(init=True, default=None)
    duration_min: int | None = field(init=True, default=None)

    @classmethod
    def from_dict(cls, dict_: dict):
        """convert from dict to BookClockLog model"""
        return cls(**{
            "id": dict_.get("id"),
            "book_id": dict_.get("book_id"),
            "clock_start": dict_.get("clock_start"),
            "clock_end": dict_.get("clock_end"),
            "duration_min": dict_.get("duration_min")
        })

    def to_dict(self, without_none_field: bool = False) -> dict:
        """convert from model to dict"""
        dict_ = {
            "id": self.id,
            "book_id": self.book_id,
            "clock_start": self.clock_start,
            "clock_end": self.clock_end,
            "duration_min": self.duration_min
        }

        if without_none_field:
            return {key: value for key, value in dict_.items() if value is not None}

        return dict_

    def to_json(self) -> str:
        """convert from model to json"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
