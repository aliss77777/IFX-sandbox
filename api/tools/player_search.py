"""
Player Search Tool

This module defines the PlayerSearchTool, a LangChain-compatible tool for searching soccer players in the fictional Huge League
using the project's vector store. It includes a schema for flexible player queries (by name, position, team, or number), supports
random/team-based queries, and provides both synchronous and asynchronous search methods. Used by the agent workflow to retrieve
player profiles, stats, and related data for downstream processing.
"""

from pydantic import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.documents import Document
from typing import Type, List, Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from data.vectorstore_singleton import get_vector_store

vector_store = get_vector_store()


class PlayerSearchSchema(BaseModel):
    query: str = Field(description=(
        "The search query to identify a soccer player in the fictional league. "
        "You can search by player name, position, or use team and number (e.g., 'Number 10 on Everglade FC'). "
        "To get random players from a team, send an asterisk '*' as the query (e.g., '* Everglade FC'). "
        "Available teams:\n"
        "  • Yucatán Force (Mérida, Mexico): Mayan pride, fortress stadium 'El Templo del Sol'.\n"
        "  • Tierra Alta FC (San José, Costa Rica): Highlanders, eco-friendly, smart play.\n"
        "  • Everglade FC (Miami, USA): Flashy, wild, South Florida flair.\n"
        "  • Fraser Valley United (Abbotsford, Canada): Vineyard roots, top youth academy."
    ))


class PlayerSearchTool(BaseTool):
    name: str = "player_search"
    args_schema: Type[BaseModel] = PlayerSearchSchema 
    description: str = (
        "Search for soccer players in the fictional league based on their name, position, or other identifying information. "
        "Returns a list of documents with player details, stats, headshots, social media links, etc. "
    )
    
    def _run(self,
             query: str,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             ) -> List[Document]:
        k = 5 if query[0] == "*" else 3
        return vector_store.similarity_search(
            query,
            k=k,
            filter=lambda doc: doc.metadata.get("type") == "player",
        )
    
    async def _arun(self,
                    query: str,
                    run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
                    ) -> List[Document]:
        k = 5 if query[0] == "*" else 3
        return await vector_store.asimilarity_search(
            query,
            k=k,
            filter=lambda doc: doc.metadata.get("type") == "player",
        )
