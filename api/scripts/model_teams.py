import os
import json
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, ClassVar
from slugify import slugify

teams = [
    {
        "name": "Yucatán Force",
        "city": "Mérida",
        "region": "Mexico",
        "description": "Deep in the Mayan heartland, this team blends cultural pride with raw talent. Their fortress-like stadium is known as El Templo del Sol — The Temple of the Sun.",
        "logo": "yucatan-force.png",
    },
    {
        "name": "Tierra Alta FC",
        "city": "San José",
        "region": "Costa Rica",
        "description": "Named for the highlands of Costa Rica, this team champions sustainability and tactical intelligence. Their lush green stadium is solar-powered and ringed by cloud forest.",
        "logo": "tierra-alta.png",
    },
    {
        "name": "Everglade FC",
        "city": "Miami",
        "region": "Florida",
        "description": "Fast, flashy, and fiercely proud of their roots in the wetlands, Everglade FC plays with flair under the humid lights of South Florida. Their style is as wild and unpredictable as the ecosystem they represent.",
        "logo": "everglade.png",
    },
    {
        "name": "Fraser Valley United",
        "city": "Abbotsford",
        "region": "British Columbia",
        "description": "Surrounded by vineyards and mountains, this team brings together rural BC pride with west coast sophistication. Known for their academy program, they're a pipeline for Canadian talent.",
        "logo": "fraser-valley.png",
    },
]


class Team(BaseModel):
    id: str
    name: str
    city: str
    region: str
    description: str 
    logo: str

    @validator("id", pre=True)
    def slugify_id(cls, v):
        return slugify(v)

    @validator("city", pre=True)
    def slugify_city(cls, v):
        return slugify(v)

    @validator("region", pre=True)
    def slugify_region(cls, v):
        return slugify(v)

    def team_vector_metadata(self):
        return {
            "type": "team",
            "name": self.name,
            "city": self.city,
            "region": self.region,
        }

    @classmethod
    def get_teams(cls):
        for team in teams:
            yield cls(id=team["name"], **team)
