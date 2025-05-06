from openai import OpenAI
import os
import csv
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Optional
import hashlib
import json
from pprint import pprint


client = OpenAI()

prompt = """
You are generating structured simulation data for a fictional soccer player.

Only return **valid JSON** that can be passed to Python's `json.loads()` without issues. Do **not** explain or wrap it in markdown. No commentary. No prose. Just raw JSON.

Here is the known player information:
{player_info}

Here is the team context:
{team_name_description}

Your task:
Generate a single flat JSON object with **exactly** the following fields — no more, no less:

```json
{{
  "height_cm":  // integer, range 150-210
  "weight_kg":  // integer, range 50-110
  "overall_rating":  // integer, range 1-100
  "is_injured":  // boolean
  "form":  // integer, range 1-10
  "goals":  // integer
  "assists":  // integer
  "yellow_cards":  // integer
  "red_cards":  // integer
  "bio":  // short paragraph; highlight signature play style, attitude, origins, or memorable traits — make it vivid, not generic
}}
```
"""

def get_ai_response(prompt):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response.output_text

# response = client.responses.create(
#     # model="gpt-4.1",
#     model="gpt-4o-mini",
#     input="Write a one-sentence bedtime story about a unicorn."
# )

# print(response.output_text)

team_descriptions = {
    'Everglade_FC_Roster.csv': 'Everglade FC — Miami, Florida Fast, flashy, and fiercely proud of their roots in the wetlands, Everglade FC plays with flair under the humid lights of South Florida. Their style is as wild and unpredictable as the ecosystem they represent.',
    'Fraser_Valley_United_Roster.csv': 'Fraser Valley United — Abbotsford, British Columbia Surrounded by vineyards and mountains, this team brings together rural BC pride with west coast sophistication. Known for their academy program, they\'re a pipeline for Canadian talent.',
    'Tierra_Alta_FC_Roster.csv': 'Tierra Alta FC — San José, Costa Rica Named for the highlands of Costa Rica, this team champions sustainability and tactical intelligence. Their lush green stadium is solar-powered and ringed by cloud forest.',
    'Yucatan_Force_Roster.csv': 'Yucatán Force — Mérida, Mexico Deep in the Mayan heartland, this team blends cultural pride with raw talent. Their fortress-like stadium is known as El Templo del Sol — The Temple of the Sun.',
}


class Player(BaseModel):
    number: int
    name: str
    age: int
    nationality: str
    shirt_number: int
    position: Literal[
        "Goalkeeper", "Left Back", "Center Back", "Right Back",
        "Full Back", "Defensive Mid", "Central Mid", "Attacking Mid",
        "Left Wing", "Right Wing", "Forward/Winger", "Striker", "Various"
    ]
    preferred_foot: Literal["Left", "Right", "Mixed"]
    role: Literal["Starter", "Bench", "Reserve/Prospect"]

    @property
    def id(self):
        if not self.team:
            raise ValueError("Team must not be empty")
        return hashlib.sha256(f"{self.team}_{self.number}".encode()).hexdigest()

    @property
    def filename(self):
        return f'{self.team.replace(" ", "_")}_{self.number}.json'
    
    # Optional flair / simulation fields
    team: Optional[str] = None
    height_cm: Optional[int] = Field(None, ge=150, le=210)
    weight_kg: Optional[int] = Field(None, ge=50, le=110)
    overall_rating: Optional[int] = Field(None, ge=1, le=100)
    is_injured: Optional[bool] = False
    form: Optional[int] = Field(None, ge=1, le=10)  # recent performance (1-10)

    # Stats placeholder — useful if you want to track across games
    goals: Optional[int] = 0
    assists: Optional[int] = 0
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0

    # Narrative hook
    bio: Optional[str] = None

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
        }

    def save(self):
        with open(os.path.join("/workspace/data/huge-league/players", self.filename), 'w') as f:
            json.dump(self.model_dump(), f)

    @classmethod
    def load(cls, filename):
        with open(os.path.join("/workspace/data/huge-league/players", filename), 'r') as f:
            data = json.load(f)
            return cls.model_validate(data)



for filename in os.listdir("/workspace/data/huge-league/rosters"):
    with open(os.path.join("/workspace/data/huge-league/rosters", filename), 'r') as f:
        print(f"Processing {filename}")
        team_description = team_descriptions.get(filename)
        team_name = " ".join(filename.split("_")[:-1])
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            player = Player.from_row(row)
            player.team = team_name
            # print('-->', player.id)
            print('-->', player)
            print('---->', player.filename)
            # print('-->', team_description)
            player_info = player.player_info()
            text = prompt.format(player_info=player_info, team_name_description=team_description)
            response = get_ai_response(text)
            # print('\n=======\n', response, '\n=======\n')

            for key, value in json.loads(response).items():
                setattr(player, key, value)
            # print(player)
            player.save()

#             break
# #         break

# # # player = Player.load("Everglade_FC_1.json")
# # # pprint(player.dict())