"""
Gradio component for displaying Team Story/News search results.
"""

import gradio as gr

def create_team_story_component(team_story_data):
    """
    Creates a Gradio HTML component to display formatted team news articles.

    Args:
        team_story_data (list): A list of dictionaries, where each dictionary 
                                  represents an article and contains keys like 
                                  'summary', 'link_to_article', and 'topic'.

    Returns:
        gr.HTML: A Gradio HTML component containing the formatted news stories.
                 Returns None if the input data is empty or invalid.
    """
    if not team_story_data or not isinstance(team_story_data, list):
        return None # Return None if no data or invalid data

    html_content = """<div style='padding: 15px; border: 1px solid #e0e0e0; border-radius: 5px; margin-top: 10px;'>
                         <h3 style='margin-top: 0; margin-bottom: 10px;'>Recent Team News</h3>"""

    for story in team_story_data:
        if isinstance(story, dict):
            summary = story.get('summary', 'No summary available.')
            link = story.get('link_to_article', '#')
            topic = story.get('topic', 'General')

            # Sanitize link to prevent basic injection issues
            safe_link = link if link.startswith(('http://', 'https://', '#')) else '#'
            
            # Escape basic HTML characters in text fields
            def escape_html(text):
                return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            safe_summary = escape_html(summary)
            safe_topic = escape_html(topic)

            html_content += f"""<div style='margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee;'>
                                    <p style='font-size: 0.9em; color: #555; margin-bottom: 5px;'><strong>Topic:</strong> {safe_topic}</p>
                                    <p style='margin-bottom: 8px;'>{safe_summary}</p>
                                    <a href='{safe_link}' target='_blank' style='font-size: 0.9em;'>Read Full Article</a>
                               </div>"""
        else:
            print(f"Warning: Skipping invalid item in team_story_data: {story}")

    # Remove the last border-bottom if content was added
    if len(team_story_data) > 0:
         last_border_pos = html_content.rfind("border-bottom: 1px solid #eee;")
         if last_border_pos != -1:
              html_content = html_content[:last_border_pos] + html_content[last_border_pos:].replace("border-bottom: 1px solid #eee;", "")

    html_content += "</div>"

    # Return None if only the initial header was created (e.g., all items were invalid)
    if html_content.strip() == """<div style='padding: 15px; border: 1px solid #e0e0e0; border-radius: 5px; margin-top: 10px;'>
                         <h3 style='margin-top: 0; margin-bottom: 10px;'>Recent Team News</h3></div>""".strip():
        return None

    return gr.HTML(html_content) 