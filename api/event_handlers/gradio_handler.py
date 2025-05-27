import queue
from colorama import Fore, Style
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs.llm_result import LLMResult
from typing import List
from langchain_core.messages import BaseMessage

TEAM_LOGO_BASE_URL = "https://huggingface.co/spaces/yamilsteven/ifx-assets/resolve/main/assets/team_logos/"

image_base = """
<div style="background-color: #1f2937; border-radius: 10px; padding: 25px; display: flex; align-items: center; width: 450px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
  <div style="margin-right: 25px;">
    <img src="https://huggingface.co/spaces/ryanbalch/IFX-huge-league/resolve/main/assets/profiles/players_pics/{filename}" alt="{filename} Pic" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #444;">
  </div>
  <div style="color: #E0E0E0;">
    <h2 style="margin-top: 0; margin-bottom: 8px; font-size: 22px; color: #FFFFFF;">{player_name} - #{player_number} (DL)</h2>
    <p style="margin: 6px 0; font-size: 15px; color: #B0B0B0;">Ht: {height} | Wt: {weight} lbs</p>
    <p style="margin: 6px 0; font-size: 15px; color: #B0B0B0;">Team: {team_name}</p>
    <p style="margin: 6px 0; font-size: 15px; color: #B0B0B0;">Experience: 6 Years</p>
    <a href="https://www.instagram.com/{instagram_url}" style="background-color: #C00000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 15px; font-size: 14px; text-align: center;">Instagram Profile</a>
  </div>
</div>
"""

game_card_html = """
<div style="text-align: center; padding: 20px; margin: 10px 0; border-radius: 8px; background-color: #1f2937; color: #FFFFFF; font-family: Arial, sans-serif; max-width: 500px; margin-left: auto; margin-right: auto;">
  <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 20px; color: #E0E0E0;">{game_title}</h3>
  <div style="display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px;">
    <div style="text-align: center; width: 40%;">
      <img src="{team1_logo_url}" 
           alt="{team_home} Logo" 
           style="max-width: 70px; max-height: 70px; margin-bottom: 5px; vertical-align: middle; display: block; margin-left: auto; margin-right: auto;" 
           onerror="this.onerror=null; this.src='{default_logo_url}';">
      <p style="font-size: 16px; font-weight: bold; margin: 5px 0;">{team_home}</p>
      <p style="font-size: 24px; font-weight: bold; margin: 0;">{team1_score}</p>
    </div>
    <p style="font-size: 20px; margin: 0 10px;">vs</p>
    <div style="text-align: center; width: 40%;">
      <img src="{team2_logo_url}" 
           alt="{team_away} Logo" 
           style="max-width: 70px; max-height: 70px; margin-bottom: 5px; vertical-align: middle; display: block; margin-left: auto; margin-right: auto;" 
           onerror="this.onerror=null; this.src='{default_logo_url}';">
      <p style="font-size: 16px; font-weight: bold; margin: 5px 0;">{team_away}</p>
      <p style="font-size: 24px; font-weight: bold; margin: 0;">{team2_score}</p>
    </div>
  </div>
  <div style="margin-top: 20px; border-top: 1px solid #555; padding-top: 15px;">
    <h4 style="margin-top: 0; margin-bottom: 10px; font-size: 16px; color: #D0D0D0; text-align: left;">Goal Highlights:</h4>
    {highlights}
  </div>
</div>
"""

team_info_card_html = """
<div style="text-align: center; padding: 50px; margin:10px 0; border-radius: 8px; background-color: #1f2937; color: #333333; max-width: 450px; margin-left: auto; margin-right: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
  <img src="{team_logo_url}" alt="{team_display_name} Logo" style="max-width: 80px; max-height: 80px; margin-bottom: 10px; display: block; margin-left: auto; margin-right: auto; border-radius: 5px;" onerror="this.onerror=null; this.src='{default_logo_url}';">
  <h3 style="margin-top: 0; margin-bottom: 8px; font-size: 22px; color: #FFFFFF;">{team_display_name}</h3>
  <p style="font-size: 15px; color: #FFFFFF; margin-bottom: 15px;">{city_display}</p>
  {team_page_cta_html}
</div>
"""

team_image_map = {
    'everglade-fc': 'Everglade_FC',
    'fraser-valley-united': 'Fraser_Valley_United',
    'tierra-alta-fc': 'Tierra_Alta_FC',
    'yucatan-force': 'Yucatan_Force',
}


class GradioEventHandler(AsyncCallbackHandler):
    """
    Example async event handler: prints streaming tokens and tool results.
    Replace with websocket or other side effects as needed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue.Queue()

    def info_box(self, message: str):
        self.queue.put(
            {
                "type": "info",
                "message": message,
            }
        )

    def ots_box(self, message: str):
        self.queue.put(
            {
                "type": "ots",
                "message": message,
            }
        )

    async def on_chat_model_start(self, *args, **kwargs):
        pass
        # self.info_box('[CHAT START]')
        # self.ots_box("""
        # <img 
        #     src="https://huggingface.co/spaces/ryanbalch/IFX-huge-league/resolve/main/assets/landing.png"
        #     style="max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: 0 auto;"
        # />
        # """)

    async def on_llm_new_token(self, token: str, **kwargs):
        if token:
            self.queue.put(token) 

    async def on_llm_end(self, result: LLMResult, *args, **kwargs):
        pass
        # if self.is_chat_stream_end(result):
        #     self.queue.put(None)

    async def on_tool_end(self, output: any, **kwargs):
        print(f"\n{Fore.CYAN}[TOOL END] {output}{Style.RESET_ALL}")
        for doc in output:
            if doc.metadata.get("show_profile_card"):
                raw_player_name = doc.metadata.get("name", "unknown-player")
                player_name = "Unknown Player"
                if raw_player_name != "unknown-player":
                    parts = raw_player_name.split('-')
                    if len(parts) == 2:
                        first_name = parts[0].capitalize()
                        last_name = parts[1].capitalize()
                        player_name = f"{last_name} {first_name}"
                    else:
                        player_name = raw_player_name.replace('-', ' ').title()
                else:
                    player_name = "Unknown Player"

                team_slug = doc.metadata.get("team", "unknown-team")
                formatted_team_name = team_slug.replace('-', ' ').title()
                if team_slug == "unknown-team":
                    formatted_team_name = "Unknown Team"
                
                player_number = doc.metadata.get("number", "N/A")
                height = doc.metadata.get("height", "175")
                weight = doc.metadata.get("weight", "150")
                instagram_url = doc.metadata.get("instagram_url", raw_player_name)

                img = image_base.format(
                    filename=self.get_image_filename(doc),
                    player_name=player_name,
                    team_name=formatted_team_name,
                    player_number=player_number,
                    height=height,
                    weight=weight,
                    instagram_url=instagram_url
                )
                self.ots_box(img)
                return

        if output and isinstance(output[0], object) and hasattr(output[0], 'metadata') and output[0].metadata.get('type') == 'event':
            game_teams_set = set()
            game_events_details = []
            raw_game_name = "Unknown Game"

            for i, doc in enumerate(output):
                if hasattr(doc, 'metadata') and doc.metadata.get('team'):
                    game_teams_set.add(doc.metadata.get('team'))
                if i == 0:
                    raw_game_name = doc.metadata.get('game_name', raw_game_name)
                
                if hasattr(doc, 'metadata') and doc.metadata.get('event') == 'Goal':
                    event_desc = doc.metadata.get('description', 'Goal scored')
                    event_minute = doc.metadata.get('minute', '')
                    event_team = doc.metadata.get('team', '')
                    game_events_details.append(f"({event_minute}') {event_team}: {event_desc}")
            
            if len(game_teams_set) >= 1:
                team_list = list(game_teams_set)
                team1_name_str = team_list[0]
                team2_name_str = team_list[1] if len(team_list) > 1 else "(opponent not specified)"

                score_team1 = 0
                score_team2 = 0
                for doc in output:
                    if hasattr(doc, 'metadata') and doc.metadata.get('event') == 'Goal':
                        scoring_team = doc.metadata.get('team')
                        if scoring_team == team1_name_str:
                            score_team1 += 1
                        elif scoring_team == team2_name_str:
                            score_team2 += 1
                
                game_title_str = raw_game_name.replace('_', ' ').title()
                highlights_html_str = "<ul style='list-style-type: none; padding-left: 0; text-align: left;'>"
                for highlight in game_events_details[:3]:
                    highlights_html_str += f"<li style='margin-bottom: 5px; font-size: 14px;'>{highlight}</li>"
                highlights_html_str += "</ul>"
                if not game_events_details:
                    highlights_html_str = "<p style='font-size: 14px;'>No goal highlights available.</p>"

                log_msg = f"Game: {game_title_str} | {team1_name_str} {score_team1} - {score_team2} {team2_name_str}"                
                team1_logo_filename = GradioEventHandler.get_team_logo_slug(team1_name_str)
                team2_logo_filename = GradioEventHandler.get_team_logo_slug(team2_name_str)

                team1_logo_url = f"{TEAM_LOGO_BASE_URL}{team1_logo_filename}"
                team2_logo_url = f"{TEAM_LOGO_BASE_URL}{team2_logo_filename}"
                default_logo_url = f"{TEAM_LOGO_BASE_URL}default.png"

                formatted_game_html = game_card_html.format(
                    game_title=game_title_str,
                    team_home=team1_name_str, 
                    team_away=team2_name_str,
                    team1_score=score_team1,
                    team2_score=score_team2,
                    highlights=highlights_html_str,
                    team1_logo_url=team1_logo_url,
                    team2_logo_url=team2_logo_url,
                    default_logo_url=default_logo_url
                )
                self.ots_box(formatted_game_html)
                return
            else:
                print(f"\n{Fore.RED}[TOOL END - GAME CARD] Not enough team data found in events.{Style.RESET_ALL}")
        
        elif isinstance(output, list) and output:
            doc_for_team_card = output[0]
            if hasattr(doc_for_team_card, 'metadata') and doc_for_team_card.metadata.get("show_team_card"):
                team_name_from_meta = doc_for_team_card.metadata.get("team_name", "Unknown Team")
                city_raw = doc_for_team_card.metadata.get("city", "N/A")
                display_team_name = str(team_name_from_meta).replace('-', ' ').replace('_', ' ').title()
                city_display = city_raw.title() if city_raw != "N/A" else "Location N/A"
                logo_filename = GradioEventHandler.get_team_logo_slug(team_name_from_meta)
                team_specific_logo_url = f"{TEAM_LOGO_BASE_URL}{logo_filename}"
                current_default_logo_url = f"{TEAM_LOGO_BASE_URL}default.png"
                team_id_slug = doc_for_team_card.metadata.get("team_id", "")
                team_page_url = f"https://www.team.com/{team_id_slug}" if team_id_slug else "#" 
                team_page_cta_html = f'''<a href="{team_page_url}" target="_blank" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 14px; margin-top: 10px;">Visit Team Page</a>'''

                formatted_team_card_html = team_info_card_html.format(
                    team_logo_url=team_specific_logo_url,
                    team_display_name=display_team_name,
                    city_display=city_display,
                    default_logo_url=current_default_logo_url,
                    team_page_cta_html=team_page_cta_html
                )
                
                self.ots_box(formatted_team_card_html)
                return

    async def on_tool_start(self, input: any, *args, **kwargs):
        self.info_box(input.get("name", "[TOOL START]"))

    async def on_workflow_end(self, state, *args, **kwargs):
        print(f"\n{Fore.CYAN}[WORKFLOW END]{Style.RESET_ALL}")
        self.queue.put(None)
        # for msg in state["messages"]:
        #     print(f'{Fore.YELLOW}{msg.content}{Style.RESET_ALL}')

    @staticmethod
    def is_chat_stream_end(result: LLMResult) -> bool:
        try:
            content = result.generations[0][0].message.content
            return bool(content and content.strip())
        except (IndexError, AttributeError):
            return False

    @staticmethod
    def get_image_filename(doc):
        return f'{team_image_map.get(doc.metadata.get("team"))}_{doc.metadata.get("number")}.png'

    @staticmethod
    def get_team_logo_slug(team_name: str) -> str:
        if not team_name or team_name == "(opponent not specified)":
            return "default.png"
        # Normalize accented for the Yucatán logo
        normalized_team_name = team_name.lower().replace('á', 'a')        
        slug = normalized_team_name.replace(' ', '-')
        return slug + ".png"
