import os
import json
from pydantic import BaseModel, Field
from typing import Literal, Optional, ClassVar
from slugify import slugify


class Event(BaseModel):
    id: str = Field(default_factory=slugify)
    game_name: str
    description: str 
    event: str
    minute: str
    player: str
    team: str

    @classmethod
    def from_row(cls, game_name: str, row_id: int, **kwargs):
        return cls(
            id=f"{game_name}_{row_id}",
            game_name=game_name,
            description=kwargs["description"],
            event=kwargs["event"],
            minute=kwargs["minute"],
            player=kwargs["player"],
            team=kwargs["team"],
        )

    def event_vector_metadata(self):
        return {
            "type": "event",
            "game_name": self.game_name,
            "description": self.description,
            "event": self.event,
            "minute": self.minute,
            "player": self.player,
            "team": self.team,
        }

    @classmethod
    def get_events(cls):
        for filename in os.listdir("/workspace/data/huge-league/games"):
            with open(os.path.join("/workspace/data/huge-league/games", filename), 'r') as f:
                data = json.load(f)
                for row_id, event in enumerate(data):
                    yield cls.from_row(game_name=filename.split(".")[0], row_id=row_id, **event)
