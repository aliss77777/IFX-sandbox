import sys
import os
# Add parent directory to path to access gradio modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gradio_llm import llm, embeddings
from gradio_graph import graph

# Create the Neo4jVector
from langchain_neo4j import Neo4jVector

neo4jvector = Neo4jVector.from_existing_index(
    embeddings,                              # (1)
    graph=graph,                             # (2)
    index_name="gameSummary",                 # (3)
    node_label="Game",                      # (4)
    text_node_property="summary",               # (5)
    embedding_node_property="embedding", # (6)
    retrieval_query="""
RETURN
    node.summary AS text,
    score,
    {
        id: node.id,
        date: node.date,
        result: node.result,
        location: node.location,
        home_team: node.home_team,
        away_team: node.away_team,
        game_id: node.game_id
    } AS metadata
"""
)

# Create the retriever
retriever = neo4jvector.as_retriever()

# Create the prompt
from langchain_core.prompts import ChatPromptTemplate

instructions = (
    "Use the given context to answer the question."
    "If you don't know the answer, say you don't know."
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

# Create the chain 
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

question_answer_chain = create_stuff_documents_chain(llm, prompt)
game_summary_retriever = create_retrieval_chain(
    retriever, 
    question_answer_chain
)

# Create a function to call the chain
def get_game_summary(input_text):
    """Function to call the chain with error handling"""
    try:
        return game_summary_retriever.invoke({"input": input_text})
    except Exception as e:
        print(f"Error in get_game_summary: {str(e)}")
        return {"output": "I apologize, but I encountered an error while searching for game summaries. Could you please rephrase your question?"}
