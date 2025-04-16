"""
Player Search - LangChain tool for retrieving player information from Neo4j

This module provides functions to:
1. Search for players in Neo4j based on natural language queries.
2. Generate text summaries about players.
3. Return both text summaries and structured data for UI components.
"""

# Import Gradio-specific modules directly
import sys
import os
# Add parent directory to path to access gradio modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gradio_llm import llm
from gradio_graph import graph
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# Create a global variable to store the last retrieved player data
# Workaround for LangChain dropping structured data
LAST_PLAYER_DATA = None

# Function to get the cached player data
def get_last_player_data():
    global LAST_PLAYER_DATA
    print(f"GETTING PLAYER DATA FROM CACHE: {LAST_PLAYER_DATA}")
    return LAST_PLAYER_DATA

# Function to set the cached player data
def set_last_player_data(player_data):
    global LAST_PLAYER_DATA
    LAST_PLAYER_DATA = player_data
    print(f"STORED PLAYER DATA IN CACHE: {player_data}")

# Clear the cache initially
set_last_player_data(None)

# Create the Cypher generation prompt for player search
PLAYER_SEARCH_TEMPLATE = """
You are an expert Neo4j Developer translating user questions about NFL players into Cypher queries.
Your goal is to find a specific player or group of players in the database based on the user's description.

Convert the user's question based on the schema provided.

IMPORTANT NOTES:
1. Always return the FULL player node with ALL its relevant properties for display.
   Specifically include: `player_id`, `Name`, `Position`, `Jersey_number`, `College`, `Height`, `Weight`, `Years_in_nfl`, `headshot_url`, `instagram_url`, `highlight_video_url`.
2. Always use case-insensitive comparisons using `toLower()` for string properties like Name, Position, College.
3. If searching by name, use CONTAINS for flexibility (e.g., `toLower(p.Name) CONTAINS toLower("bosa")`).
4. If searching by number, ensure the number property (`p.Jersey_number`) is matched correctly (it's likely stored as an integer or string, check schema).
5. NEVER use the embedding property.
6. Limit results to 1 if the user asks for a specific player, but allow multiple for general queries (e.g., "list all QBs"). Default to LIMIT 5 if multiple results are possible and no limit is specified.

Example Questions and Queries:

1. "Who is Nick Bosa?"
```
MATCH (p:Player)
WHERE toLower(p.Name) CONTAINS toLower("Nick Bosa")
RETURN p.player_id, p.Name, p.Position, p.Jersey_number, p.College, p.Height, p.Weight, p.Years_in_nfl, p.headshot_url, p.instagram_url, p.highlight_video_url
LIMIT 1
```

2. "Tell me about player number 13"
```
MATCH (p:Player)
WHERE p.Jersey_number = 13 OR p.Jersey_number = "13" // Adapt based on schema type
RETURN p.player_id, p.Name, p.Position, p.Jersey_number, p.College, p.Height, p.Weight, p.Years_in_nfl, p.headshot_url, p.instagram_url, p.highlight_video_url
LIMIT 1
```

3. "List all quarterbacks"
```
MATCH (p:Player)
WHERE toLower(p.Position) = toLower("QB")
RETURN p.player_id, p.Name, p.Position, p.Jersey_number, p.College, p.Height, p.Weight, p.Years_in_nfl, p.headshot_url, p.instagram_url, p.highlight_video_url
ORDER BY p.Name
LIMIT 5
```

4. "Find players from Central Florida"
```
MATCH (p:Player)
WHERE toLower(p.College) CONTAINS toLower("Central Florida")
RETURN p.player_id, p.Name, p.Position, p.Jersey_number, p.College, p.Height, p.Weight, p.Years_in_nfl, p.headshot_url, p.instagram_url, p.highlight_video_url
ORDER BY p.Name
LIMIT 5
```

Schema:
{schema}

Question:
{question}
"""

player_search_prompt = PromptTemplate.from_template(PLAYER_SEARCH_TEMPLATE)

# Create the player summary generation prompt
PLAYER_SUMMARY_TEMPLATE = """
You are a helpful AI assistant providing information about an NFL player.
Based on the following data, write a concise 1-2 sentence summary.
Focus on their name, position, and maybe college or experience.

Data:
- Name: {Name}
- Position: {Position}
- Number: {Jersey_number}
- College: {College}
- Experience (Years): {Years_in_nfl}

Write the summary:
"""

player_summary_prompt = PromptTemplate.from_template(PLAYER_SUMMARY_TEMPLATE)

# Create the Cypher QA chain for player search
player_search_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=player_search_prompt,
    return_direct=True,  # Return raw results
    allow_dangerous_requests=True
)

# Function to parse player data from Cypher result
def parse_player_data(result):
    """Parse the player data from the Cypher result into a structured dictionary."""
    if not result or not isinstance(result, list) or len(result) == 0:
        print("Parsing player data: No result found.")
        return None

    # Assuming the query returns one player row or we take the first if multiple
    player = result[0]
    print(f"Parsing player data: Raw result item: {player}")

    # Extract properties using the defined map, checking ONLY for the prefixed keys
    parsed_data = {}
    # Corrected key map to use lowercase property names matching Cypher output
    key_map = {
        # Key from Cypher result : Key for output dictionary
        'p.player_id': 'player_id',
        'p.name': 'Name', # Corrected case
        'p.position': 'Position', # Corrected case
        'p.jersey_number': 'Jersey_number', # Corrected case
        'p.college': 'College', # Corrected case
        'p.height': 'Height', # Corrected case
        'p.weight': 'Weight', # Corrected case
        'p.years_in_nfl': 'Years_in_nfl', # Corrected case
        'p.headshot_url': 'headshot_url',
        'p.instagram_url': 'instagram_url',
        'p.highlight_video_url': 'highlight_video_url'
    }

    for cypher_key, dict_key in key_map.items():
        if cypher_key in player:
            parsed_data[dict_key] = player[cypher_key]
        # else: # Optional: Log if a specific key wasn't found
        #     print(f"Parsing player data: Key '{cypher_key}' not found in result.")

    # Ensure essential keys were successfully mapped
    if 'Name' not in parsed_data or 'player_id' not in parsed_data:
        print("Parsing player data: Essential keys ('Name', 'player_id') were not successfully mapped from result.")
        print(f"Available keys in result: {list(player.keys())}")
        return None

    print(f"Parsing player data: Parsed dictionary: {parsed_data}")
    return parsed_data

# Function to generate a player summary using LLM
def generate_player_summary(player_data):
    """Generate a natural language summary of the player using the LLM."""
    if not player_data:
        return "I couldn't retrieve enough information to summarize the player."

    try:
        # Format the prompt with player data, providing defaults
        formatted_prompt = player_summary_prompt.format(
            Name=player_data.get('Name', 'N/A'),
            Position=player_data.get('Position', 'N/A'),
            Jersey_number=player_data.get('Jersey_number', 'N/A'),
            College=player_data.get('College', 'N/A'),
            Years_in_nfl=player_data.get('Years_in_nfl', 'N/A')
        )

        # Generate the summary using the LLM
        summary = llm.invoke(formatted_prompt)
        summary_content = summary.content if hasattr(summary, 'content') else str(summary)
        print(f"Generated Player Summary: {summary_content}")
        return summary_content
    except Exception as e:
        print(f"Error generating player summary: {str(e)}")
        return f"Summary for {player_data.get('Name', 'this player')}."

# Main function to search for a player and generate output
def player_search_qa(input_text: str) -> dict:
    """
    Searches for a player based on input text, generates a summary, and returns data.

    Args:
        input_text (str): Natural language query about a player.

    Returns:
        dict: Response containing text summary and structured player data.
    """
    global LAST_PLAYER_DATA
    set_last_player_data(None) # Clear cache at the start of each call

    try:
        # Log the incoming query
        print(f"--- Processing Player Search Query: {input_text} ---")

        # Search for the player using the Cypher chain
        search_result = player_search_chain.invoke({"query": input_text})
        print(f"Raw search result from chain: {search_result}")

        # Check if we have a result and it's not empty
        if not search_result or not search_result.get('result') or not isinstance(search_result['result'], list) or len(search_result['result']) == 0:
            print("Player Search: No results found in Neo4j.")
            return {
                "output": "I couldn't find information about that player. Could you be more specific or try a different name/number?",
                "player_data": None
            }

        # Parse the player data from the first result
        player_data = parse_player_data(search_result['result'])

        if not player_data:
            print("Player Search: Failed to parse data from Neo4j result.")
            return {
                "output": "I found some information, but couldn't process the player details correctly.",
                "player_data": None
            }

        # Generate the text summary
        summary_text = generate_player_summary(player_data)

        # Store the structured data in the cache for the UI component
        set_last_player_data(player_data)

        # Return both the text summary and the structured data
        final_output = {
            "output": summary_text,
            "player_data": player_data # Include for potential direct use if caching fails
        }
        print(f"Final player_search_qa output: {final_output}")
        return final_output

    except Exception as e:
        print(f"Error in player_search_qa: {str(e)}")
        import traceback
        traceback.print_exc()
        set_last_player_data(None) # Clear cache on error
        return {
            "output": "I encountered an error while searching for the player. Please try again.",
            "player_data": None
        } 