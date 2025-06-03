from functools import lru_cache
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore


@lru_cache(maxsize=1)
def get_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    return InMemoryVectorStore.load(
        "/code/data/vectorstore.json", embedding=embeddings
    )
