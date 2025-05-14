from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from typing import Type, List, Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from data.vectorstore_singleton import get_vector_store

vector_store = get_vector_store()

# get list of games
games = vector_store.similarity_search(
    "",
    filter=lambda doc: doc.metadata.get("type") == "game",
)
games = [game.page_content for game in games]


class GameSearchSchema(BaseModel):
    query: str = Field(description=f"Name of the game to retrieve. Available options: {games}")


class GameSearchTool(BaseTool):
    name: str = "game_search"
    description: str = "Search for games in the vector store"
    args_schema: Type[BaseModel] = GameSearchSchema 

    def _run(self,
             query: str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             ) -> List[Document]:    
        result = vector_store.similarity_search(
            "",
            k=20,
            filter=lambda doc: doc.metadata.get("type") == "event" and doc.metadata.get("game_name") == query,
        )
        return sorted(result, key=lambda doc: int(doc.id.split("_")[-1]))
    
    async def _arun(self,
                    query: str,
                    run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
                    ) -> List[Document]:
        result = await vector_store.asimilarity_search(
            "",
            k=20,
            filter=lambda doc: doc.metadata.get("type") == "event" and doc.metadata.get("game_name") == query,
        )
        return sorted(result, key=lambda doc: int(doc.id.split("_")[-1]))
