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

# Generate images for all players
for player in Player.get_players():
    print(player.name)
    print(player.profile_pic)
    response = generate_image(player.profile_pic)
    player.save_image(response)
    break
