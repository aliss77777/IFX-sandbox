# Agent system prompt
AGENT_SYSTEM_PROMPT = """
You are a 49ers expert providing information about the football team, players, and fans.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to the 49ers, players, or fans.

Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.

IMPORTANT TOOL SELECTION GUIDELINES:
1. For ANY 49ers-specific questions about players, games, schedules, fans, or team info, ALWAYS use the "49ers Graph Search" tool first
2. ONLY use "Game Summary Search" for detailed game summaries or specific match results
3. ONLY use "General Football Chat" for non-49ers football questions

When in doubt, default to using "49ers Graph Search" for any 49ers-related questions.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Example 1:
User: "Who is the quarterback for the 49ers?"
Thought: This is asking about a specific 49ers player position, so I should use the 49ers Graph Search tool.
Action: 49ers Graph Search
Action Input: Who is the quarterback for the 49ers?

Example 2:
User: "Tell me about the last game against the Seahawks"
Thought: This is asking for details about a specific game, so I should use the Game Summary Search tool.
Action: Game Summary Search
Action Input: Tell me about the last game against the Seahawks

Example 3:
User: "How does the NFL draft work?"
Thought: This is asking about general NFL rules, not specific to the 49ers, so I should use the General Football Chat tool.
Action: General Football Chat
Action Input: How does the NFL draft work?

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
"""

# Chat prompt for general conversation
CHAT_SYSTEM_PROMPT = """
You are a 49ers expert providing information about the football team, players, and fans.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to the 49ers, players, or fans.
""" 

SAMPLE_QUERIES = """
A) Basic Entity Exploration

A1) Count All Nodes
```
MATCH (n)
RETURN labels(n) AS nodeLabels, count(*) AS total
```

A2) List All Players
```
MATCH (p:Player)
RETURN p.name AS playerName, p.position AS position, p.jersey_number AS jerseyNumber
ORDER BY p.jersey_number
```

A3) List All Games
```
MATCH (g:Game)
RETURN g.game_id AS gameId, g.date AS date, g.location AS location, 
       g.home_team AS homeTeam, g.away_team AS awayTeam, g.result AS finalScore
ORDER BY g.date
```

A4) List All Fan Communities
```
MATCH (c:Community)
RETURN c.fan_chapter_name, c.city, c.state
ORDER BY c.fan_chapter_name
```

A5) List All Fans
```
MATCH (f:Fan)
RETURN f.fan_id AS fanId, f.first_name AS firstName, 
       f.last_name AS lastName, f.email AS email
LIMIT 20
```

B) Relationship & Network Analysis

B1) Which Players Are Most Favorited by Fans?
```
MATCH (f:Fan)-[:FAVORITE_PLAYER]->(p:Player)
RETURN p.name AS playerName, count(f) AS fanCount
ORDER BY fanCount DESC
LIMIT 5
```

B2) Which Communities Have the Most Members?
```
MATCH (f:Fan)-[:MEMBER_OF]->(c:Community)
RETURN c.fan_chapter_name AS chapterName, count(f) AS fanCount
ORDER BY fanCount DESC
LIMIT 5
```

B3) Find All Fans Who Both Favorite a Specific Player AND Are in a Specific Community
```
MATCH (f:Fan)-[:FAVORITE_PLAYER]->(p:Player { name: "Nick Bosa" })
MATCH (f)-[:MEMBER_OF]->(c:Community { fan_chapter_name: "Niner Empire Hawaii 808" })
RETURN f.first_name AS firstName, f.last_name AS lastName, c.fan_chapter_name AS community
```

C) Game & Schedule Queries

C1) Upcoming Home Games
```
MATCH (g:Game)
WHERE g.home_team = "San Francisco 49ers"
RETURN g.date AS date, g.location AS location, g.away_team AS awayTeam
ORDER BY date
```

C2) Search for Past Results
```
MATCH (g:Game)
WHERE g.result IS NOT NULL
RETURN g.date AS date, g.home_team AS home, g.away_team AS away, g.result AS finalScore
ORDER BY date DESC
LIMIT 5
```

C3) Games Played in a Specific Location
```
MATCH (g:Game { location: "Levi's Stadium" })
RETURN g.date AS date, g.home_team AS homeTeam, g.away_team AS awayTeam, g.result AS finalScore
```

D) Fan & Community Scenarios

D1) Find Fans in the Same Community
```
MATCH (f:Fan)-[:MEMBER_OF]->(c:Community { fan_chapter_name: "Bay Area 49ers Fans" })
RETURN f.first_name AS firstName, f.last_name AS lastName
ORDER BY lastName
```

D2) Locate Community Email Contacts
```
MATCH (c:Community)
RETURN c.fan_chapter_name AS chapter, c.email_contact AS email
ORDER BY chapter
```

D3) Show Which Fans Have Not Joined Any Community
```
MATCH (f:Fan)
WHERE NOT (f)-[:MEMBER_OF]->(:Community)
RETURN f.first_name AS firstName, f.last_name AS lastName, f.email AS email
```
"""
