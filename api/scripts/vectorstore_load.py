import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from model_player import Player
from model_games import Event
from model_teams import Team

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# vector_store = InMemoryVectorStore.load("/code/data/vectorstore.json", embedding=embeddings)
vector_store = InMemoryVectorStore(embeddings)

# add players
print("Adding players...")
for player in Player.get_players():
    print('-->',player.id)
    doc = Document(
        id=player.id,
        page_content=json.dumps(player.model_dump()),
        metadata=player.player_vector_metadata(),
    )
    vector_store.add_documents([doc])

# add events
print("Adding events...")
games = []
for event in Event.get_events():
    print('-->',event.id)
    if event.game_name not in games:
        games.append(event.game_name)
        doc = Document(
            id=event.game_name,
            page_content=event.game_name,
            metadata={"type": "game"},
        )
        vector_store.add_documents([doc])

    doc = Document(
        id=event.id,
        page_content=json.dumps(event.model_dump()),
        metadata=event.event_vector_metadata(),
    )
    vector_store.add_documents([doc])

# add teams
print("Adding teams...")
for team in Team.get_teams():
    print('-->',team.id)
    doc = Document(
        id=team.id,
        page_content=json.dumps(team.model_dump()),
        metadata=team.team_vector_metadata(),
    )
    vector_store.add_documents([doc])

print("Saving vector store...")
vector_store.dump("/code/data/vectorstore.json")
