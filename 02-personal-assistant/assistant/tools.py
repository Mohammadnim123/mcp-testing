import os

from langchain_core.tools import tool
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings

_vector_store = None


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        embeddings = PineconeEmbeddings(model="llama-text-embed-v2")
        _vector_store = PineconeVectorStore.from_existing_index(
            index_name=os.environ["PINECONE_INDEX"],
            embedding=embeddings,
        )
    return _vector_store


@tool
def search_knowledge_base(query: str) -> str:
    """Searches the internal knowledge base for technical info and documentation. Use this when you need to find information from uploaded PDF documents."""
    store = get_vector_store()
    results = store.similarity_search(query, k=10)
    if not results:
        return "No relevant information found in the knowledge base."
    return "\n---\n".join(doc.page_content for doc in results)
