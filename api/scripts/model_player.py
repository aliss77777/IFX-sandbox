import json
import os
from typing import ClassVar, Literal, Optional

from pydantic import BaseModel, Field
from slugify import slugify


class Player(BaseModel):
    teams: ClassVar[list[str]] = [
        "Fraser Valley United",
        "Everglade FC",
        "Yucatan Force",
        "Tierra Alta FC",
    ]
    number: int
    name: str
    age: int
    nationality: str
    shirt_number: int
    position: Literal[
        "Goalkeeper",
        "Left Back",
        "Center Back",
        "Right Back",
        "Full Back",
        "Defensive Mid",
        "Central Mid",
        "Attacking Mid",
        "Left Wing",
        "Right Wing",
        "Forward/Winger",
        "Striker",
        "Various",
    ]
    preferred_foot: Literal["Left", "Right", "Mixed"]
    role: Literal["Starter", "Bench", "Reserve/Prospect"]

    @property
    def id(self):
        if not self.team:
            raise ValueError("Team must not be empty")
        # return hashlib.sha256(f"{self.team}_{self.number}".encode()).hexdigest()
        return slugify(f"{self.team}_{self.number}")

    @property
    def filename(self):
        return f"{self.team.replace(' ', '_')}_{self.number}.json"

    # Optional flair / simulation fields
    team: Optional[str] = None
    height_cm: Optional[int] = Field(None, ge=150, le=210)
    weight_kg: Optional[int] = Field(None, ge=50, le=110)
    overall_rating: Optional[int] = Field(None, ge=1, le=100)
    is_injured: Optional[bool] = False
    is_captain: Optional[bool] = False
    form: Optional[int] = Field(None, ge=1, le=10)  # recent performance (1-10)

    # Stats placeholder — useful if you want to track across games
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0

    # Narrative hook
    bio: Optional[str] = None

    # AI-generated profile pic
    profile_pic: Optional[str] = None

    @classmethod
    def from_row(cls, row):
        if len(row) != 8:
            raise ValueError("Row must have 8 elements")
        return cls(
            number=row[0],
            name=row[1],
            position=row[2],
            age=row[3],
            nationality=row[4],
            shirt_number=row[5],
            preferred_foot=row[6],
            role=row[7],
        )

    def player_info(self):
        return {
            "number": self.number,
            "name": self.name,
            "position": self.position,
            "age": self.age,
            "nationality": self.nationality,
            "shirt_number": self.shirt_number,
            "preferred_foot": self.preferred_foot,
            "role": self.role,
            "is_captain": self.is_captain,
        }

    def player_vector_metadata(self):
        return {
            "type": "player",
            "number": self.number,
            "name": slugify(self.name),
            "position": slugify(self.position),
            "age": self.age,
            "nationality": slugify(self.nationality),
            "shirt_number": self.shirt_number,
            "preferred_foot": slugify(self.preferred_foot),
            "role": slugify(self.role),
            "team": slugify(self.team),
            "is_captain": self.is_captain,
        }

    def save(self):
        with open(
            os.path.join("/workspace/data/huge-league/players", self.filename), "w"
        ) as f:
            json.dump(self.model_dump(exclude_none=True), f, indent=4)

    @classmethod
    def load(cls, filename):
        with open(
            os.path.join("/workspace/data/huge-league/players", filename), "r"
        ) as f:
            data = json.load(f)
            return cls.model_validate(data)

    @classmethod
    def get_players(cls, team=None):
        for filename in os.listdir("/workspace/data/huge-league/players"):
            if not filename.endswith(".json"):
                continue
            player = cls.load(filename)
            if team and player.team != team:
                continue
            yield player

    @classmethod
    def get_player_by_number(cls, team_name: str, player_number: int):
        for player in cls.get_players(team=team_name):
            if player.number == player_number:
                return player
        return None

    @classmethod
    def get_captain(cls, team_name: str):
        for player in cls.get_players(team=team_name):
            if player.is_captain:
                return player
        return None

    def update_captain_status(self, is_captain: bool):
        self.is_captain = is_captain
        captain_bio_text = " He is the team captain."
        if is_captain:
            if self.bio and captain_bio_text not in self.bio:
                self.bio += captain_bio_text
            elif not self.bio:
                self.bio = f"{self.name}{captain_bio_text}."
        else:
            if self.bio and captain_bio_text in self.bio:
                self.bio = self.bio.replace(captain_bio_text, "").strip()
        self.save()

    def save_image(self, image_bytes):
        filename = self.filename.replace(".json", ".png")
        with open(
            os.path.join("/workspace/data/huge-league/players_pics", filename), "wb"
        ) as f:
            f.write(image_bytes)
