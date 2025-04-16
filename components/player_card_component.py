import gradio as gr
import html

def create_player_card_component(player_data=None):
    """
    Creates a Gradio HTML component to display player information based on test.ipynb structure.

    Args:
        player_data (dict, optional): Dictionary containing player data.
                                      Expected keys: 'Name', 'Position', 'Jersey_number', 
                                      'headshot_url', 'College', 'Height', 'Weight',
                                      'Years_in_nfl', 'instagram_url'. Defaults to None.

    Returns:
        gr.HTML: A Gradio HTML component displaying the player card, or empty if no data.
    """
    print("--- Entered create_player_card_component ---") # DEBUG LOG
    if not player_data or not isinstance(player_data, dict):
        print("Component received no player data, returning empty.") # DEBUG LOG
        return gr.HTML("")

    print(f"Component received player_data: {player_data}") # DEBUG LOG

    try:
        # Extract data with defaults, using html.escape
        name = html.escape(player_data.get('Name', 'N/A'))
        position = html.escape(player_data.get('Position', ''))
        number = html.escape(str(player_data.get('Jersey_number', '')))
        headshot_url = html.escape(player_data.get('headshot_url', ''))
        college = html.escape(player_data.get('College', 'N/A'))
        height = html.escape(player_data.get('Height', 'N/A'))
        weight = html.escape(player_data.get('Weight', 'N/A'))
        exp = html.escape(str(player_data.get('Years_in_nfl', 'N/A')))
        instagram_url = html.escape(player_data.get('instagram_url', ''))

        # CSS from test.ipynb, adapted slightly for theme integration
        css = """
        <style>
            .player-card-container {
                /* Add a container to allow for centering or specific placement */
                padding: 10px 0;
            }
            .player-card {
                background-color: #222222; /* Dark background */
                border: 1px solid #333333;
                margin: 0.5rem auto; /* Center card */
                padding: 1rem;
                border-radius: 8px;
                width: 320px; /* Slightly wider */
                box-sizing: border-box;
                font-family: 'Arial', sans-serif;
                color: #E6E6E6; /* Light text */
                overflow: hidden; /* Clear float */
                 box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            .player-photo {
                width: 80px;
                height: 80px;
                background-color: #444; /* Darker placeholder */
                float: left;
                margin-right: 1rem;
                border-radius: 50%; /* Make it round */
                object-fit: cover; /* Cover ensures image fills circle */
                border: 2px solid #B3995D; /* Gold accent */
            }
            .card-content {
                float: left;
                width: calc(100% - 100px); /* Adjust width considering photo and margin */
            }
            .card-content h4 {
                margin: 0 0 0.5rem 0;
                font-size: 1.2em;
                color: #FFFFFF; /* White name */
                font-weight: bold;
            }
            .card-content ul {
                margin: 0.25rem 0;
                padding-left: 1.2rem;
                list-style: none; /* Remove default bullets */
                font-size: 0.9em;
                color: #B0B0B0;
            }
             .card-content ul li {
                margin-bottom: 4px; /* Space between list items */
             }
            .player-social-link {
                margin-top: 10px;
                clear: both; /* Ensure it appears below floated elements if needed */
            }
            .player-social-link a {
                display: inline-block;
                text-decoration: none;
                color: #FFFFFF;
                background-color: #AA0000; /* 49ers Red */
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 0.8em;
                transition: background-color 0.2s ease;
            }
            .player-social-link a:hover {
                background-color: #B3995D; /* Gold accent on hover */
            }
        </style>
        """

        # HTML structure based on test.ipynb
        # Using an outer container for better layout control in Gradio
        html_content = f"""
        {css}
        <div class="player-card-container">
            <div class="player-card">
                <img src="{headshot_url}" class="player-photo" alt="{name} Headshot" onerror="this.style.display='none'" />
                <div class="card-content">
                    <h4>{name} {f'- #{number}' if number else ''} {f'({position})' if position else ''}</h4>
                    <ul>
                        <li>Ht: {height} | Wt: {weight} lbs</li>
                        <li>College: {college}</li>
                        <li>Experience: {exp} Years</li>
                    </ul>
        """
        # Add Instagram link conditionally
        if instagram_url:
             html_content += f"""
                    <div class="player-social-link">
                        <a href="{instagram_url}" target="_blank">Instagram Profile</a>
                    </div>
            """

        html_content += """
                </div>
            </div>
        </div>
        """
        
        print(f"Component generated HTML (first 100 chars): {html_content[:100]}...") # DEBUG LOG
        return gr.HTML(html_content)

    except Exception as e:
        print(f"Error creating player card component: {str(e)}")
        # Return a simple error message component
        return gr.HTML("<div style='padding: 1rem; color: red;'>⚠️ Error loading player card.</div>")

# Example Usage (for testing component independently if needed)
# if __name__ == '__main__':
#     example_data = {
#         'Name': 'Brock Purdy',
#         'headshot_url': 'https://a.espncdn.com/i/headshots/nfl/players/full/4433216.png', # Example URL
#         'instagram_url': 'https://www.instagram.com/brock.purdy13/',
#         'Position': 'QB',
#         'Number': '13'
#     }
#     component = create_player_card_component(example_data)
# 
#     with gr.Blocks() as demo:
#         gr.Markdown("## Player Card Example")
#         demo.add(component)
# 
#     demo.launch() 