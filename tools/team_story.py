"""
Tool for querying Neo4j about recent team news stories.
"""

import os
import sys
import re # Import regex for cleaning Cypher query
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
# from langchain_openai import ChatOpenAI # No longer needed directly here
# from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain # Removed import

# Adjust path to import graph object and LLM from the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from gradio_graph import graph  # Import the configured graph instance
    from gradio_llm import llm      # Import the configured LLM instance
except ImportError as e:
    print(f"Error importing graph or llm: {e}")
    print("Please ensure gradio_graph.py and gradio_llm.py exist and are configured correctly.")
    sys.exit(1)

# Load environment variables if needed (though graph/llm should be configured)
load_dotenv()

# Define the prompt for translating NL query to Cypher for Team Story
CYPHER_TEAM_STORY_GENERATION_TEMPLATE = """
Task: Generate Cypher query to query a graph database for team news stories.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}

Based on the schema, generate a Cypher query that retrieves relevant :Team_Story nodes based on the user's question.
*   Focus on searching the `summary` and `topic` properties of the :Team_Story node (aliased as `s`).
*   Always `MATCH (s:Team_Story)` and potentially relate it `MATCH (s)-[:STORY_ABOUT]->(t:Team {{name: 'San Francisco 49ers'}})` if the query implies 49ers context.
*   Use `toLower()` for case-insensitive matching on properties like `topic` or keywords in `summary`.
*   Return relevant properties like `s.summary`, `s.link_to_article`, `s.topic`.
*   Limit the results to a reasonable number (e.g., LIMIT 10).

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher query.
Do not include any text except the generated Cypher query. Output ONLY the Cypher query.

The question is:
{query}

Cypher Query:
"""

CYPHER_TEAM_STORY_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "query"], template=CYPHER_TEAM_STORY_GENERATION_TEMPLATE
)

# Placeholder for structured data caching
LAST_TEAM_STORY_DATA = []

def get_last_team_story_data():
    """Returns the structured data from the last team story query."""
    return LAST_TEAM_STORY_DATA

def clean_cypher_query(query_text):
    """ Basic cleaning of LLM-generated Cypher query. """
    # Remove ```cypher ... ``` markdown fences if present
    match = re.search(r"```(?:cypher)?\s*(.*?)\s*```", query_text, re.DOTALL | re.IGNORECASE)
    if match:
        query = match.group(1).strip()
    else:
        query = query_text.strip()
    # Remove potential leading/trailing quotes if the LLM added them
    query = query.strip('"\'')
    return query

def team_story_qa(query: str) -> dict:
    """
    Queries the Neo4j database for team news stories based on the user query.
    Manually generates Cypher, executes it, and formats the results.
    Args:
        query: The natural language query from the user.
    Returns:
        A dictionary containing the 'output' text and structured 'team_story_data'.
    """
    global LAST_TEAM_STORY_DATA
    LAST_TEAM_STORY_DATA = [] # Clear previous results
    structured_results = []
    output_text = "Sorry, I encountered an error trying to find team news."

    print(f"--- Running Team Story QA for query: {query} ---")

    try:
        # 1. Generate Cypher query using LLM
        print("Generating Cypher query...")
        cypher_generation_result = llm.invoke(
            CYPHER_TEAM_STORY_GENERATION_PROMPT.format(
                schema=graph.schema, 
                query=query
            )
        )
        generated_cypher = cypher_generation_result.content # Extract text content
        cleaned_cypher = clean_cypher_query(generated_cypher)
        print(f"Generated Cypher (cleaned):\n{cleaned_cypher}")

        # 2. Execute the generated Cypher query
        if cleaned_cypher:
            print("Executing Cypher query...")
            # Assuming the generated query doesn't need parameters for now
            # If parameters are needed, the prompt/parsing would need adjustment
            neo4j_results = graph.query(cleaned_cypher)
            print(f"Neo4j Results: {neo4j_results}")

            # 3. Process results and extract structured data
            if neo4j_results:
                for record in neo4j_results:
                     # Check if record is a dictionary (expected from graph.query)
                     if isinstance(record, dict):
                        story_data = {
                            'summary': record.get('s.summary', 'Summary not available'),
                            'link_to_article': record.get('s.link_to_article', '#'),
                            'topic': record.get('s.topic', 'Topic not available')
                        }
                        # Basic check if data seems valid
                        if story_data['link_to_article'] != '#': 
                            structured_results.append(story_data)
                     else:
                         print(f"Warning: Skipping unexpected record format: {record}")
        else:
            print("Warning: No Cypher query was generated.")
            output_text = "I couldn't formulate a query to find the specific news you asked for."

        # --- Limit the number of results stored and returned --- #
        MAX_STORIES_TO_SHOW = 3 
        LAST_TEAM_STORY_DATA = structured_results[:MAX_STORIES_TO_SHOW] 
        # --- End limiting --- #
        
        # 4. Format the text output based on the limited structured results
        if not LAST_TEAM_STORY_DATA: # Check the potentially limited list now
             # Keep default error or no-query message unless results were empty after valid query
             if cleaned_cypher and not neo4j_results:
                 output_text = "I found no specific news articles matching your query in the database."
             elif not cleaned_cypher:
                  pass # Keep the "couldn't formulate" message
             else: # Error occurred during query execution or processing
                 pass # Keep the default error message
        else:
             # Base the text output on the *limited* list
             output_text = "Here's what I found related to your query:\n\n"
             for i, story in enumerate(LAST_TEAM_STORY_DATA): # Iterate over the limited list
                 output_text += f"{i+1}. {story['summary']}\n[Link: {story['link_to_article']}]\n\n"
             # Optionally, mention if more were found originally (before limiting)
             if len(structured_results) > MAX_STORIES_TO_SHOW:
                 output_text += f"... displaying the top {MAX_STORIES_TO_SHOW} of {len(structured_results)} relevant articles found."

    except Exception as e:
        import traceback
        print(f"Error during team_story_qa: {e}")
        print(traceback.format_exc()) # Print full traceback for debugging
        output_text = "Sorry, I encountered an unexpected error trying to find team news."
        LAST_TEAM_STORY_DATA = [] # Ensure cache is clear on error

    print(f"--- Team Story QA output: {output_text} ---")
    print(f"--- Team Story QA structured data: {LAST_TEAM_STORY_DATA} ---")
    
    return {"output": output_text, "team_story_data": LAST_TEAM_STORY_DATA}

# Example usage (for testing)
if __name__ == '__main__':
    # Ensure graph and llm are available for standalone testing if needed
    print("Testing team_story_qa...")
    test_query = "What is the latest news about the 49ers draft?"
    print(f"\nTesting with query: {test_query}")
    response = team_story_qa(test_query)
    print("\nResponse Text:")
    print(response.get("output"))
    # print("\nStructured Data:")
    # print(response.get("team_story_data"))

    test_query_2 = "Any updates on the roster?"
    print(f"\nTesting with query: {test_query_2}")
    response_2 = team_story_qa(test_query_2)
    print("\nResponse Text:")
    print(response_2.get("output"))
    # print("\nStructured Data:")
    # print(response_2.get("team_story_data"))

    test_query_3 = "Tell me about non-existent news"
    print(f"\nTesting with query: {test_query_3}")
    response_3 = team_story_qa(test_query_3)
    print("\nResponse Text:")
    print(response_3.get("output"))
    # print("\nStructured Data:")
    # print(response_3.get("team_story_data")) 