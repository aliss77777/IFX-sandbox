from llm import llm
from graph import graph

# Create the Cypher QA chain
from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about the 49ers team, players, games, fans, and communities.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Do not return entire nodes or embedding properties.

IMPORTANT: Always use case-insensitive comparisons in your Cypher queries by applying toLower() to both the property and the search string, or by using the =~ operator with (?i) for case-insensitive regex matching. This ensures that user queries match regardless of capitalization.

Example Cypher Statements for 49ers Graph:

1. Count All Nodes:
MATCH (n)
RETURN labels(n) AS nodeLabels, count(*) AS total

2. List All Players:
MATCH (p:Player)
RETURN p.name AS playerName, p.position AS position, p.jersey_number AS jerseyNumber
ORDER BY p.jersey_number

3. List All Games:
MATCH (g:Game)
RETURN g.game_id AS gameId, g.date AS date, g.location AS location, 
       g.home_team AS homeTeam, g.away_team AS awayTeam, g.result AS finalScore
ORDER BY g.date

4. List All Fan Communities:
MATCH (c:Community)
RETURN c.fan_chapter_name, c.city, c.state
ORDER BY c.fan_chapter_name

5. List All Fans:
MATCH (f:Fan)
RETURN f.fan_id AS fanId, f.first_name AS firstName, 
       f.last_name AS lastName, f.email AS email
LIMIT 20

6. Most Favorited Players:
MATCH (f:Fan)-[:FAVORITE_PLAYER]->(p:Player)
RETURN p.name AS playerName, count(f) AS fanCount
ORDER BY fanCount DESC
LIMIT 5

7. Communities with Most Members:
MATCH (f:Fan)-[:MEMBER_OF]->(c:Community)
RETURN c.fan_chapter_name AS chapterName, count(f) AS fanCount
ORDER BY fanCount DESC
LIMIT 5

8. Find Fans Favoriting a Specific Player & Community (Case-Insensitive):
MATCH (f:Fan)-[:FAVORITE_PLAYER]->(p:Player)
WHERE toLower(p.name) = toLower("Nick Bosa")
MATCH (f)-[:MEMBER_OF]->(c:Community)
WHERE toLower(c.fan_chapter_name) = toLower("Niner Empire Hawaii 808")
RETURN f.first_name AS firstName, f.last_name AS lastName, c.fan_chapter_name AS community

9. Upcoming Home Games (Case-Insensitive):
MATCH (g:Game)
WHERE toLower(g.home_team) = toLower("San Francisco 49ers")
RETURN g.date AS date, g.location AS location, g.away_team AS awayTeam
ORDER BY date

10. Past Game Results:
MATCH (g:Game)
WHERE g.result IS NOT NULL
RETURN g.date AS date, g.home_team AS home, g.away_team AS away, g.result AS finalScore
ORDER BY date DESC
LIMIT 5

11. Games Played at a Specific Location (Case-Insensitive):
MATCH (g:Game)
WHERE toLower(g.location) = toLower("Levi's Stadium")
RETURN g.date AS date, g.home_team AS homeTeam, g.away_team AS awayTeam, g.result AS finalScore

12. Find Fans in a Specific Community (Case-Insensitive):
MATCH (f:Fan)-[:MEMBER_OF]->(c:Community)
WHERE toLower(c.fan_chapter_name) = toLower("Bay Area 49ers Fans")
RETURN f.first_name AS firstName, f.last_name AS lastName
ORDER BY lastName

12b. Find Fans in a Community (Using Regex, Case-Insensitive):
MATCH (f:Fan)-[:MEMBER_OF]->(c:Community)
WHERE c.fan_chapter_name =~ '(?i).*bay area.*'
RETURN f.first_name AS firstName, f.last_name AS lastName
ORDER BY lastName

13. Community Email Contacts:
MATCH (c:Community)
RETURN c.fan_chapter_name AS chapter, c.email_contact AS email
ORDER BY chapter

14. Fans Without a Community:
MATCH (f:Fan)
WHERE NOT (f)-[:MEMBER_OF]->(:Community)
RETURN f.first_name AS firstName, f.last_name AS lastName, f.email AS email

15. Case-Insensitive Player Search:
MATCH (p:Player)
WHERE toLower(p.position) = toLower("QB")  // Case-insensitive position filter
RETURN p.name AS playerName, p.position AS position, p.jersey_number AS jerseyNumber
ORDER BY p.jersey_number

16. Case-Insensitive Team Search:
MATCH (g:Game)
WHERE toLower(g.away_team) CONTAINS toLower("seahawks")  // Case-insensitive team search
RETURN g.date AS date, g.home_team AS home, g.away_team AS away, g.result AS finalScore
ORDER BY date DESC

Schema:
{schema}

Question:
{question}
"""


cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt,
    allow_dangerous_requests=True
)

def cypher_qa_wrapper(input_text):
    """Wrapper function to handle input format and potential errors"""
    try:
        # Log the incoming query for debugging
        print(f"Processing query: {input_text}")
        
        # Process the query through the Cypher QA chain
        result = cypher_qa.invoke({"query": input_text})
        
        # If we have access to the generated Cypher query, we could modify it here
        # to ensure case-insensitivity, but the GraphCypherQAChain already executes
        # the query. Instead, we rely on the prompt engineering approach to ensure
        # the LLM generates case-insensitive queries.
        
        # Log the result for debugging
        if "intermediate_steps" in result:
            generated_cypher = result["intermediate_steps"][0]["query"]
            print(f"Generated Cypher query: {generated_cypher}")
        
        return result
    except Exception as e:
        print(f"Error in cypher_qa: {str(e)}")
        return {"output": "I apologize, but I encountered an error while searching the database. Could you please rephrase your question?"}


''' Testing Utilities we might run later '''
def run_test_query(query_name):
    """Run predefined test queries from test_cases.txt
    
    Args:
        query_name (str): Identifier for the query to run, e.g., "players", "games", "favorite_players"
    
    Returns:
        dict: Results from the query execution
    """
    test_queries = {
        "count_nodes": """
            MATCH (n)
            RETURN labels(n) AS nodeLabels, count(*) AS total
        """,
        "players": """
            MATCH (p:Player)
            RETURN p.name AS playerName, p.position AS position, p.jersey_number AS jerseyNumber
            ORDER BY p.jersey_number
        """,
        "games": """
            MATCH (g:Game)
            RETURN g.date AS date, g.location AS location, g.home_team AS homeTeam, 
                   g.away_team AS awayTeam, g.result AS finalScore
            ORDER BY g.date
        """,
        "communities": """
            MATCH (c:Community)
            RETURN c.fan_chapter_name AS chapterName, c.city AS city, c.state AS state, 
                   c.email_contact AS contactEmail
            ORDER BY c.fan_chapter_name
        """,
        "fans": """
            MATCH (f:Fan)
            RETURN f.first_name AS firstName, f.last_name AS lastName, f.email AS email
            LIMIT 20
        """,
        "favorite_players": """
            MATCH (f:Fan)-[:FAVORITE_PLAYER]->(p:Player)
            RETURN p.name AS playerName, count(f) AS fanCount
            ORDER BY fanCount DESC
            LIMIT 5
        """,
        "community_members": """
            MATCH (f:Fan)-[:MEMBER_OF]->(c:Community)
            RETURN c.fan_chapter_name AS chapterName, count(f) AS memberCount
            ORDER BY memberCount DESC
        """
    }
    
    if query_name in test_queries:
        try:
            # Execute the query directly using the graph connection
            result = graph.query(test_queries[query_name])
            return {"output": result}
        except Exception as e:
            print(f"Error running test query '{query_name}': {str(e)}")
            return {"output": f"Error running test query: {str(e)}"}
    else:
        return {"output": f"Test query '{query_name}' not found. Available queries: {', '.join(test_queries.keys())}"}
