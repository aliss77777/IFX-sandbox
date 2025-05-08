from pprint import pprint
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore.load("/code/data/vectorstore.json", embedding=embeddings)

# query = "ryan brown"
# query = "defensive midfielder"
query = "goaly"
results = vector_store.similarity_search(query, k=3)

for result in results:
    pprint(result.page_content)
    print("---")
