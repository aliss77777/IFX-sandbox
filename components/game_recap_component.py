import gradio as gr
import pandas as pd
import os

def create_game_recap_component(game_data=None):
    """
    Creates a Gradio component to display game information.
    Args:
        game_data (dict, optional): Game data to display. If None, loads from CSV.
    Returns:
        gr.Column: A Gradio component displaying the game recap.
    """
    try:
        # Load game schedule if no game data provided
        if game_data is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            schedule_path = os.path.join(current_dir, "data", "april_11_multimedia_data_collect", "schedule_with_result_and_logo_urls.csv")
            df = pd.read_csv(schedule_path)
            game_data = df.iloc[0].to_dict()  # Get first game

        # Extract game details
        match_number = game_data.get('Match Number', 'N/A')
        date = game_data.get('Date', 'N/A')
        location = game_data.get('Location', 'N/A')
        home_team = game_data.get('Home Team', 'N/A')
        away_team = game_data.get('Away Team', 'N/A')
        home_logo = game_data.get('home_team_logo_url', '')
        away_logo = game_data.get('away_team_logo_url', '')
        result = game_data.get('Result', 'N/A')
        game_outcome = game_data.get('game_result', 'N/A')

        # Determine winner
        winner = None
        if result != 'N/A':
            home_score, away_score = map(int, result.split('-'))
            winner = home_team if home_score > away_score else away_team

        # Create the component
        with gr.Column(elem_classes=["game-recap-container"]) as game_recap:
            # Date and Location
            gr.Markdown(f"### Game {match_number} - {date}")
            gr.Markdown(f"**Location:** {location}")

            # Teams and Scores
            with gr.Row(elem_classes=["game-recap-row"]):
                # Home Team
                with gr.Column(elem_classes=["team-info"]):
                    if home_logo:
                        gr.Image(home_logo, elem_classes=["team-logo"])
                    gr.Markdown(f"**{home_team}**", elem_classes=["team-name"] + (["winner"] if winner == home_team else []))
                    gr.Markdown(result.split('-')[0], elem_classes=["team-score"])

                # Away Team
                with gr.Column(elem_classes=["team-info"]):
                    if away_logo:
                        gr.Image(away_logo, elem_classes=["team-logo"])
                    gr.Markdown(f"**{away_team}**", elem_classes=["team-name"] + (["winner"] if winner == away_team else []))
                    gr.Markdown(result.split('-')[1], elem_classes=["team-score"])

            # Game Outcome
            if game_outcome != 'N/A':
                gr.Markdown(f"**{game_outcome}**")

            # Video Highlights (placeholder)
            with gr.Row(elem_classes=["video-preview"]):
                gr.Markdown("🎥 Video highlights coming soon...")

        return game_recap

    except Exception as e:
        print(f"Error creating game recap component: {str(e)}")
        # Return a simple error message component
        with gr.Column() as error_component:
            gr.Markdown("⚠️ Error loading game recap. Please try again later.")
        return error_component

# Test the component when run directly
if __name__ == "__main__":
    demo = gr.Blocks()
    with demo:
        game_recap = create_game_recap_component()
    demo.launch() 