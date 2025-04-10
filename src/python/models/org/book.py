# model/org/book.py
from dataclasses import dataclass, field
import json

from models import Model


@dataclass
class Book(Model):
    """Book model"""
    id: int | None = field(init=True, default=None)
    title: str | None = field(init=True, default=None)
    priority: str | None = field(init=True, default=None)
    effort: float | None = field(init=True, default=None)
    created_at: str | None = field(init=True, default=None)
    ended_at: str | None = field(init=True, default=None)
    scheduled_at: str | None = field(init=True, default=None)
    deadline_at: str | None = field(init=True, default=None)
    tags: str | None = field(init=True, default=None)
    notes: str | None = field(init=True, default=None)

    @classmethod
    def from_dict(cls, dict_: dict):
        """convert from dict to Book model"""
        return cls(**{
            "id": dict_.get("id"),
            "title": dict_.get("title"),
            "priority": dict_.get("priority"),
            "effort": dict_.get("effort"),
            "created_at": dict_.get("created_at"),
            "ended_at": dict_.get("ended_at"),
            "scheduled_at": dict_.get("scheduled_at"),
            "deadline_at": dict_.get("deadline_at"),
            "tags": dict_.get("tags"),
            "notes": dict_.get("notes")
        })

    def to_dict(self, without_none_field: bool = False) -> dict:
        """convert from model to dict"""
        dict_ = {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "effort": self.effort,
            "created_at": self.created_at,
            "ended_at": self.ended_at,
            "scheduled_at": self.scheduled_at,
            "deadline_at": self.deadline_at,
            "tags": self.tags,
            "notes": self.notes
        }

        if without_none_field:
            return {key: value for key, value in dict_.items() if value is not None}

        return dict_

    def to_json(self) -> str:
        """convert from model to json"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
