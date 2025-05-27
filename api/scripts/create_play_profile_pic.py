from openai import OpenAI
import base64
from model_player import Player

client = OpenAI()


def get_ai_response(prompt):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )
    return response.output_text


def generate_image(prompt):
    result = client.images.generate(
        model="gpt-image-1",
        size="1024x1024",
        quality="medium",
        prompt=prompt
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    return image_bytes


prompt_a = """
You are generating a realistic portrait of a fictional professional soccer player using their structured profile data.

Use the information below to inform the player's:
- Physical build (age, height, weight)
- Facial features and vibe (bio, nationality, personality)
- Team kit details (team name, role, position)
- Pose and mood (based on form, rating, injury status)

Be creative, but grounded in realism — think press photo or matchday portrait.

Here is the player profile:

{player_profile}

Your output should describe only the image to be generated. No text, captions, or extra commentary. Just a detailed image prompt.
"""

# result = client.images.generate(
#     model="gpt-image-1",
#     size="1024x1024",
#     quality="medium",
#     prompt=prompt
# )

# image_base64 = result.data[0].b64_json
# image_bytes = base64.b64decode(image_base64)

# # Generate profile pic descriptions for all players
# for player in Player.get_players():
#     print(player.name)
#     # print(player.profile_pic)
#     if not player.profile_pic:
#         print("--> generate pic description")
#         text = prompt_a.format(player_profile=player.model_dump())
#         response = get_ai_response(text)
#         print(response)
#         player.profile_pic = response
#         player.save()
#     else:
#         print("--> skip")
#     # break


image_prompt = """
A realistic studio-style headshot portrait of {profile[name]}, a {profile[age]}-year-old professional soccer player from {profile[nationality]}. He plays as a {profile[position]} and currently wears jersey number {profile[shirt_number]} for the {team_name} soccer team. 

He is wearing the team's official kit: a {shirt_color} jersey, clean and well-fitted, featuring his number {profile[shirt_number]} on the front. The image should capture a calm and confident expression, suitable for official media. The player has a well-groomed appearance, facing forward with even lighting and a neutral or softly blurred backdrop in studio conditions. No action pose, just a clear, professional profile suitable for player bio pages or trading cards.
"""

shirt_colors = {
    "Everglade FC": "emerald green",
    "Fraser Valley United": "dark red",
    "Yucatan Force": "dark orange",
    "Tierra Alta FC": "spring green",
}

# Generate images for all players
for player in Player.get_players():
    print(player.name)
    # print(player.player_info())
    shirt_color = shirt_colors[player.team]
    text = image_prompt.format(
        profile=player.player_info(),
        team_name=player.team,
        shirt_color=shirt_color)
    # print(text)
    # print(player.profile_pic)
    response = generate_image(text)
    player.save_image(response)
