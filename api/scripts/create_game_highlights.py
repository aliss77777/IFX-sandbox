from openai import OpenAI
import base64
from model_player import Player
import json

client = OpenAI()


def get_ai_response(prompt):
    response = client.responses.create(
        model="gpt-4o",
        input=prompt
    )
    return response.output_text


def player_to_dict(player):
    return {
        "name": player.name,
        "position": player.position,
        "shirt_number": player.shirt_number,
        "preferred_foot": player.preferred_foot,
        "role": player.role,
        "form": player.form,
    }


prompt = """
You are simulating a fictional soccer match and creating a realistic event timeline from kickoff to final whistle.

Here is the match context:
- Match type: {match_type}
- Location: {location}
- Date: {date}
- Home team: {home_team}
- Away team: {away_team}
- Winner: {winner}
- Score: {score}

Here is the {home_team} roster:
{home_roster}

Here is the {away_team} roster:
{away_roster}

Rules:
- Spread out events across 90+ minutes
- Substitutions should use players not in the starting 11 if available
- Vary event types and timing

Only return a JSON array of chronological match events, formatted exactly like this example:

[
  {{
    "minute": // string, e.g. 45+2
    "team": // home or away team name
    "event": // e.g. Goal, Yellow Card, Substitution, etc.
    "player": // name + number
    "description": // 1-sentence summary
  }}
]
"""


# # match 1
# match_type = "semifinal 1"
# location = "El Templo del Sol (fictional stadium in Mérida, Mexico)"
# date = "July 10, 2025"
# home_team = Player.teams[2]
# away_team = Player.teams[3]
# winner = Player.teams[2]
# score = "2–1"
# home_roster = None
# away_roster = None 


# match 2
match_type = "semifinal 2"
location = "Everglade Arena (fictional stadium in Miami, Florida)"
date = "July 11, 2025"
home_team = Player.teams[1]
away_team = Player.teams[0]
winner = Player.teams[1]
score = "3-3 (4-2 pens)"
home_roster = None
away_roster = None 

home_players = Player.get_players(team=home_team)
away_players = Player.get_players(team=away_team)

home_roster = [player_to_dict(player) for player in home_players]
away_roster = [player_to_dict(player) for player in away_players]

prompt = prompt.format(
    match_type=match_type,
    location=location,
    date=date,
    home_team=home_team,
    away_team=away_team,
    home_roster=home_roster,
    away_roster=away_roster,
    winner=winner,
    score=score,
)

# print(prompt)

response = get_ai_response(prompt)

# Parse the AI response as JSON
try:
    if response.startswith("```json") and response.endswith("```"):
        response = response[7:-3]
    events = json.loads(response)
except Exception as e:
    print("Error parsing AI response as JSON:", e)
    print("Raw response was:\n", response)
    raise

# Pretty-print JSON to terminal
print(json.dumps(events, indent=4, sort_keys=True))

# Write pretty JSON to file
with open(f"/workspace/data/huge-league/games/{match_type.replace(' ', '_')}.json", "w") as f:
    json.dump(events, f, indent=4, sort_keys=True)

# Optionally, if you want a more human-readable text format, uncomment below:
# def pretty_print_events(events):
#     for event in events:
#         print(f"[{event['minute']}] {event['team']} - {event['event']} - {event['player']}: {event['description']}")
# pretty_print_events(events)

