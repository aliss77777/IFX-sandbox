from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore.load(
    "/code/data/vectorstore.json", embedding=embeddings
)

# query = "ryan brown"
# query = "defensive midfielder"
query = "Everglade FC team captain"
results = vector_store.similarity_search(query, k=3)
results = vector_store.similarity_search(
    query,
    k=3,
    filter=lambda doc: doc.metadata.get("type") == "player",
)

for result in results:
    # pprint(result.page_content)
    print(
        f"{result.metadata['number']} - {result.metadata['team']} - captain: {result.metadata['is_captain']}"
    )
    if result.metadata["number"] == 9:
        print(result.page_content)
        print(result.metadata["raw"])
    print("---")
