import gradio as gr
import pandas as pd
import os
import html

def create_game_recap_component(game_data=None):
    """
    Creates a Gradio component to display game information with a simple table layout.
    Args:
        game_data (dict, optional): Game data to display. If None, loads from CSV.
    Returns:
        gr.HTML: A Gradio component displaying the game recap.
    """
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load game schedule if no game data provided
        if game_data is None:
            # Try to load from the April 11 final data which includes highlight videos
            schedule_path = os.path.join(current_dir, "data", "april_11_multimedia_data_collect", 
                                        "new_final_april 11", "schedule_with_result_april_11.csv")
            if not os.path.exists(schedule_path):
                # Fallback to the other schedule file
                schedule_path = os.path.join(current_dir, "data", "april_11_multimedia_data_collect", 
                                            "schedule_with_result_and_logo_urls.csv")
            
            df = pd.read_csv(schedule_path)
            # use a single game for testing
            game_row = df[df['Match Number'] == 92]
            if len(game_row) > 0:
                game_data = game_row.iloc[0].to_dict()
            else:
                game_data = df.iloc[0].to_dict()  # Fallback to first game

        # Extract game details
        match_number = game_data.get('Match Number', 'N/A')
        date = game_data.get('Date', 'N/A')
        location = game_data.get('Location', 'N/A')
        
        # Handle different column naming conventions between CSV files
        home_team = game_data.get('Home Team', game_data.get('HomeTeam', 'N/A'))
        away_team = game_data.get('Away Team', game_data.get('AwayTeam', 'N/A'))
        
        # Get team logo URLs
        home_logo = game_data.get('home_team_logo_url', '')
        away_logo = game_data.get('away_team_logo_url', '')
        
        # Get result and determine scores
        result = game_data.get('Result', 'N/A')
        home_score = away_score = 'N/A'
        
        if result != 'N/A':
            scores = result.split('-')
            if len(scores) == 2:
                home_score = scores[0].strip()
                away_score = scores[1].strip()
        
        # Determine winner for highlighting
        winner = None
        if result != 'N/A':
            try:
                home_score_int = int(home_score)
                away_score_int = int(away_score)
                winner = 'home' if home_score_int > away_score_int else 'away'
            except ValueError:
                winner = None
        
        # Get highlight video URL
        highlight_video_url = game_data.get('highlight_video_url', '')
        
        # Create a simple HTML table layout
        html_content = f"""
        <style>
            .game-recap-table {{
                width: 100%;
                border-collapse: collapse;
                border: 1px solid #ddd;
                border-radius: 8px;
                overflow: hidden;
                margin: 20px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            
            .team-cell {{
                padding: 15px;
                text-align: left;
                vertical-align: middle;
                border-bottom: 1px solid #eee;
            }}
            
            .team-logo {{
                width: 40px;
                height: 40px;
                object-fit: contain;
                margin-right: 10px;
                border-radius: 50%;
                vertical-align: middle;
            }}
            
            .team-name {{
                display: inline-block;
                vertical-align: middle;
            }}
            
            .team-name-main {{
                font-weight: bold;
                font-size: 18px;
                display: block;
            }}
            
            .team-name-sub {{
                font-size: 14px;
                color: #666;
                display: block;
            }}
            
            .score-cell {{
                padding: 15px;
                text-align: right;
                font-size: 32px;
                font-weight: bold;
                vertical-align: middle;
                width: 80px;
            }}
            
            .winner-indicator {{
                color: #ff6b00;
                margin-left: 5px;
            }}
            
            .video-cell {{
                background: linear-gradient(135deg, #e31837 0%, #e31837 50%, #4f2683 50%, #4f2683 100%);
                color: white;
                padding: 20px;
                text-align: center;
                vertical-align: middle;
            }}
            
            .vs-container {{
                margin-bottom: 15px;
            }}
            
            .vs-logo {{
                width: 30px;
                height: 30px;
                object-fit: contain;
                margin: 0 5px;
                border-radius: 50%;
                background-color: rgba(255,255,255,0.2);
                vertical-align: middle;
            }}
            
            .vs-text {{
                font-weight: bold;
                margin: 0 5px;
            }}
            
            .recap-text {{
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .video-link {{
                display: inline-block;
                padding: 8px 15px;
                background-color: rgba(255,255,255,0.2);
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 10px;
            }}
            
            .video-link:hover {{
                background-color: rgba(255,255,255,0.3);
            }}
        </style>
        
        <table class="game-recap-table">
            <tr>
                <td class="team-cell">
                    <img src="{html.escape(away_logo)}" alt="{html.escape(away_team)} logo" class="team-logo">
                    <div class="team-name">
                        <span class="team-name-main">{html.escape(away_team.split(' ')[0] if ' ' in away_team else away_team)}</span>
                        <span class="team-name-sub">{html.escape(away_team.split(' ', 1)[1] if ' ' in away_team else '')}</span>
                    </div>
                </td>
                <td class="score-cell">
                    {away_score}{' <span class="winner-indicator">▶</span>' if winner == 'away' else ''}
                </td>
                <td class="video-cell" rowspan="2">
                    <div class="vs-container">
                        <img src="{html.escape(away_logo)}" alt="{html.escape(away_team)} logo" class="vs-logo">
                        <span class="vs-text">VS</span>
                        <img src="{html.escape(home_logo)}" alt="{html.escape(home_team)} logo" class="vs-logo">
                    </div>
                    <div class="recap-text">Recap</div>
                    {f'<a href="{html.escape(highlight_video_url)}" target="_blank" class="video-link">Watch Highlights</a>' if highlight_video_url else ''}
                </td>
            </tr>
            <tr>
                <td class="team-cell">
                    <img src="{html.escape(home_logo)}" alt="{html.escape(home_team)} logo" class="team-logo">
                    <div class="team-name">
                        <span class="team-name-main">{html.escape(home_team.split(' ')[0] if ' ' in home_team else home_team)}</span>
                        <span class="team-name-sub">{html.escape(home_team.split(' ', 1)[1] if ' ' in home_team else '')}</span>
                    </div>
                </td>
                <td class="score-cell">
                    {home_score}{' <span class="winner-indicator">▶</span>' if winner == 'home' else ''}
                </td>
            </tr>
        </table>
        """
        
        return gr.HTML(html_content)

    except Exception as e:
        print(f"Error creating game recap component: {str(e)}")
        # Return a simple error message component
        return gr.HTML("<div style='padding: 1rem; color: red;'>⚠️ Error loading game recap. Please try again later.</div>")

# Test the component when run directly
if __name__ == "__main__":
    demo = gr.Blocks()
    with demo:
        game_recap = create_game_recap_component()
    demo.launch(share=True)
