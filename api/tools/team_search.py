"""
Team Search Tool

This module defines the TeamSearchTool, a LangChain-compatible tool for searching soccer teams 
in the fictional Huge League using the project's vector store.
"""

from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_core.documents import Document
from typing import Type, List, Optional
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from data.vectorstore_singleton import get_vector_store

vector_store = get_vector_store()


class TeamSearchInputSchema(BaseModel):
    team_query: str = Field(description=(
        "The search query to identify a soccer team in the fictional league. "
    ))

class TeamSearchTool(BaseTool):
    name: str = "team_search"
    description: str = (
        "Searches for a specific soccer team in the fictional league based on its name. "
        "Returns information about the team, which can be used to display a team card."
    )
    args_schema: Type[BaseModel] = TeamSearchInputSchema
    
    def _run(
        self,
        team_query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Document]:
        """Search for a team using the vector store."""
        results = vector_store.similarity_search(
            query=team_query,
            k=1,
            filter=lambda doc: doc.metadata.get("type") == "team",
        )
        
        processed_results = []
        for doc in results:
            team_name_found = doc.metadata.get("name", team_query) 
            
            doc.metadata["show_team_card"] = True
            doc.metadata["team_name"] = team_name_found
            doc.metadata.pop("country", None)
            doc.metadata.pop("description", None)
            if "city" not in doc.metadata:
                doc.metadata["city"] = "N/A"

            processed_results.append(doc)
        
        return processed_results
    
    async def _arun(
        self,
        team_query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> List[Document]:
        """Asynchronously searches for a team using the vector store."""
        found_docs = await vector_store.asimilarity_search(
            query=team_query, 
            k=3,
            metadata={"type": "team"}  # Use metadata filter instead of filter function
        )
        
        processed_results = []
        if found_docs:
            doc = found_docs[0] 
            if doc.metadata.get("type") == "team" and doc.metadata.get("name"):
                metadata = {
                    "show_team_card": True,
                    "team_name": doc.metadata.get("name", "Unknown Team"),
                    "team_id": doc.metadata.get("id", doc.metadata.get("name", "unknown-id").lower().replace(" ", "-")),
                    "city": doc.metadata.get("city", "N/A"),
                }
                page_content = f"Found: {metadata['team_name']}. Location: {metadata.get('city')}."
                processed_doc = Document(page_content=page_content, metadata=metadata)
                processed_results.append(processed_doc)
            else:
                print(f"Found document for query '{team_query}' but it's not a valid team entry or lacks name.")

        if not processed_results:
            print(f"No team found for query: {team_query} after vector search and filtering.")

        return processed_results
