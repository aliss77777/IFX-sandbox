from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from typing import Type, List

from data.vectorstore_singleton import get_vector_store

vector_store = get_vector_store()


class PlayerSearchSchema(BaseModel):
    query: str = Field(description="The search query to identify a player. Examples: 'Deebo Samuel', '49ers QB', 'Number 19 on the 49ers'")


class PlayerSearchTool(BaseTool):
    name: str = "player_search"
    description: str = "Search for players in the vector store"
    args_schema: Type[BaseModel] = PlayerSearchSchema 
    description: str = "Search for players in the vector store based on their name, position, or other identifying information. Returns a list of documents with player details, stats, headshots, social media links, etc."
    
    def _run(self, query: str) -> List[Document]:
        return vector_store.similarity_search(
            query,
            k=3,
            filter={"type": "player"},
        )
    
    async def _arun(self, query: str) -> List[Document]:
        return vector_store.asimilarity_search(
            query,
            k=3,
            filter={"type": "player"},
        )
