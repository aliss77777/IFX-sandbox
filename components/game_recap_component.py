import gradio as gr
import pandas as pd
import os
import html

def create_game_recap_component(game_data=None):
    """
    Creates a Gradio component to display game information with a simple table layout.
    Args:
        game_data (dict, optional): Game data to display. If None, returns an empty component.
    Returns:
        gr.HTML: A Gradio component displaying the game recap.
    """
    try:
        # If no game data provided, return an empty component
        if game_data is None or not isinstance(game_data, dict):
            return gr.HTML("")
        
        # Extract game details
        match_number = game_data.get('match_number', game_data.get('Match Number', 'N/A'))
        date = game_data.get('date', 'N/A')
        location = game_data.get('location', 'N/A')
        
        # Handle different column naming conventions between sources
        home_team = game_data.get('home_team', game_data.get('Home Team', game_data.get('HomeTeam', 'N/A')))
        away_team = game_data.get('away_team', game_data.get('Away Team', game_data.get('AwayTeam', 'N/A')))
        
        # Get team logo URLs
        home_logo = game_data.get('home_team_logo_url', '')
        away_logo = game_data.get('away_team_logo_url', '')
        
        # Get result and determine scores
        result = game_data.get('result', 'N/A')
        home_score = game_data.get('home_score', 'N/A')
        away_score = game_data.get('away_score', 'N/A')
        
        # If we don't have separate scores but have result, try to parse it
        if (home_score == 'N/A' or away_score == 'N/A') and result != 'N/A':
            scores = result.split('-')
            if len(scores) == 2:
                home_score = scores[0].strip()
                away_score = scores[1].strip()
        
        # Determine winner for highlighting
        winner = game_data.get('winner')
        if not winner and result != 'N/A':
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
                background: #ffffff; /* replaced the gradient with solid white */
                color: #333;         /* changed from white to a darker color for visibility */
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
                color: #AA0000 !important; /* 49ers primary red from your design system */
            }}
            
            .video-link {{
                display: inline-block;
                padding: 8px 15px;
                background-color: #AA0000;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 10px;
            }}
            
            .video-link:hover {{
                background-color: #B3995D;
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

# Function to process a game recap response from the agent
def process_game_recap_response(response):
    """
    Process a response from the agent that may contain game recap data.
    
    Args:
        response (dict): The response from the agent
        
    Returns:
        tuple: (text_output, game_data)
            - text_output (str): The text output to display
            - game_data (dict or None): Game data for the visual component or None
    """
    try:
        # Check if the response has game_data directly
        if isinstance(response, dict) and "game_data" in response:
            return response.get("output", ""), response.get("game_data")
        
        # Check if game data is in intermediate steps (where LangChain often puts tool outputs)
        if isinstance(response, dict) and "intermediate_steps" in response:
            steps = response.get("intermediate_steps", [])
            for step in steps:
                # Check the observation part of the step, which contains the tool output
                if isinstance(step, list) and len(step) >= 2:
                    observation = step[1]  # Second element is typically the observation
                    if isinstance(observation, dict) and "game_data" in observation:
                        return observation.get("output", response.get("output", "")), observation.get("game_data")
                
                # Alternative format where step might be a dict with observation key
                if isinstance(step, dict) and "observation" in step:
                    observation = step["observation"]
                    if isinstance(observation, dict) and "game_data" in observation:
                        return observation.get("output", response.get("output", "")), observation.get("game_data")
        
        # If it's just a text response
        if isinstance(response, str):
            return response, None
        
        # Default case for other response types
        if isinstance(response, dict):
            return response.get("output", ""), None
        
        return str(response), None
        
    except Exception as e:
        print(f"Error processing game recap response: {str(e)}")
        import traceback
        traceback.print_exc()  # Add stack trace for debugging
        return "I encountered an error processing the game data. Please try again.", None

# Test function for running the component directly
if __name__ == "__main__":
    # Create sample game data for testing
    test_game_data = {
        'game_id': 'test-game-123',
        'date': '10/09/2024',
        'location': "Levi's Stadium",
        'home_team': 'San Francisco 49ers',
        'away_team': 'New York Jets',
        'home_score': '32',
        'away_score': '19',
        'result': '32-19',
        'winner': 'home',
        'home_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png',
        'away_team_logo_url': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png',
        'highlight_video_url': 'https://www.youtube.com/watch?v=igOb4mfV7To'
    }
    
    # Create a test Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("# Game Recap Component Test")
        
        with gr.Row():
            game_recap = create_game_recap_component(test_game_data)
            
        with gr.Row():
            clear_btn = gr.Button("Clear Component")
            show_btn = gr.Button("Show Component")
        
        clear_btn.click(lambda: None, None, game_recap)
        show_btn.click(lambda: test_game_data, None, game_recap)
    
    demo.launch(share=True)
