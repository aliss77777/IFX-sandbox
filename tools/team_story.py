"""
Tool for querying Neo4j about recent team news stories.
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain

# Adjust path to import graph object and LLM from the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from gradio_graph import graph  # Import the configured graph instance
    from gradio_llm import llm  # Import the configured LLM instance
except ImportError as e:
    print(f"Error importing graph or llm: {e}")
    print("Please ensure gradio_graph.py and gradio_llm.py exist and are configured correctly.")
    sys.exit(1)

# Load environment variables if needed (though graph/llm should be configured)
load_dotenv()

# Define the prompt for translating NL query to Cypher for Team Story
CYPHER_TEAM_STORY_GENERATION_TEMPLATE = """
Task: Generate Cypher query to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher query.
Do not include any text except the generated Cypher query.

The question is:
{query}

Cypher Query:
"""

CYPHER_TEAM_STORY_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "query"], template=CYPHER_TEAM_STORY_GENERATION_TEMPLATE
)

# Placeholder for structured data caching (similar to player_search/game_recap)
LAST_TEAM_STORY_DATA = []

def get_last_team_story_data():
    """Returns the structured data from the last team story query."""
    return LAST_TEAM_STORY_DATA

def team_story_qa(query: str) -> dict:
    """
    Queries the Neo4j database for team news stories based on the user query.

    Args:
        query: The natural language query from the user.

    Returns:
        A dictionary containing the 'output' text and potentially structured 'team_story_data'.
    """
    global LAST_TEAM_STORY_DATA
    LAST_TEAM_STORY_DATA = [] # Clear previous results

    print(f"--- Running Team Story QA for query: {query} ---")

    try:
        # Initialize the QA chain for Team Story
        team_story_chain = GraphCypherQAChain.from_llm(
            llm=llm,                  # Use the pre-configured LLM
            graph=graph,              # Use the pre-configured graph connection
            cypher_prompt=CYPHER_TEAM_STORY_GENERATION_PROMPT,
            verbose=True,             # Set to True for debugging Cypher generation
            return_intermediate_steps=True, # Useful for debugging
            return_direct=False # Return the final answer directly? Set to False for now
        )
        
        # Use the GraphCypherQAChain to get results
        # The chain handles NL -> Cypher -> Execution -> LLM response generation
        result = team_story_chain.invoke({"query": query})
        
        print(f"Raw result from team_story_chain: {result}")

        # Extract relevant info (summaries, links) from the result['intermediate_steps']
        # This structure depends on GraphCypherQAChain's output
        # Typically intermediate_steps contains context (list of dicts)
        structured_results = []
        if 'intermediate_steps' in result and isinstance(result['intermediate_steps'], list):
            for step in result['intermediate_steps']:
                if 'context' in step and isinstance(step['context'], list):
                     for item in step['context']:
                          # Assuming item is a dict representing a :Team_Story node
                          if isinstance(item, dict):
                            story_data = {
                                'summary': item.get('s.summary', 'Summary not available'),
                                'link_to_article': item.get('s.link_to_article', '#'),
                                'topic': item.get('s.topic', 'Topic not available')
                            }
                            structured_results.append(story_data)

        LAST_TEAM_STORY_DATA = structured_results
        
        # Format the text output
        if not structured_results:
             output_text = result.get('result', "I couldn't find any specific news articles matching your query, but I can try a broader search.")
        else:
             # Simple text formatting for now
             output_text = result.get('result', "Here's what I found:") + "\n\n"
             for i, story in enumerate(structured_results[:3]): # Show top 3
                 output_text += f"{i+1}. {story['summary']}\n[Link: {story['link_to_article']}]\n\n"
             if len(structured_results) > 3:
                 output_text += f"... found {len(structured_results)} relevant articles in total."

    except Exception as e:
        print(f"Error during team_story_qa: {e}")
        output_text = "Sorry, I encountered an error trying to find team news."
        LAST_TEAM_STORY_DATA = []

    print(f"--- Team Story QA output: {output_text} ---")
    print(f"--- Team Story QA structured data: {LAST_TEAM_STORY_DATA} ---")
    
    # Return both text output and structured data (though structured data isn't used by agent yet)
    return {"output": output_text, "team_story_data": LAST_TEAM_STORY_DATA}

# Example usage (for testing)
if __name__ == '__main__':
    test_query = "What is the latest news about the 49ers draft?"
    print(f"Testing team_story_qa with query: {test_query}")
    response = team_story_qa(test_query)
    print("\nResponse:")
    print(response.get("output"))
    print("\nStructured Data:")
    print(response.get("team_story_data"))

    test_query_2 = "Any updates on the roster?"
    print(f"\nTesting team_story_qa with query: {test_query_2}")
    response_2 = team_story_qa(test_query_2)
    print("\nResponse:")
    print(response_2.get("output"))
    print("\nStructured Data:")
    print(response_2.get("team_story_data")) 