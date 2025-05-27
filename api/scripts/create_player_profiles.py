from openai import OpenAI
import os
import csv
import json
from pprint import pprint
from model_player import Player

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


if __name__ == "__main__":
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