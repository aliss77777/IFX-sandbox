from pprint import pprint
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore.load("/code/data/vectorstore.json", embedding=embeddings)

# query = "ryan brown"
# query = "defensive midfielder"
query = "* FC Everglade"
results = vector_store.similarity_search(query, k=3)
results = vector_store.similarity_search(
    query,
    k=3,
    filter=lambda doc: doc.metadata.get("type") == "player",
)

for result in results:
    pprint(result.page_content)
    print("---")
