import os

from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

_vector_store = None
COLLECTION = "assistant_kb"


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name=COLLECTION,
            embedding_function=FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5"),
            persist_directory=os.environ.get("CHROMA_PATH", "./chroma_db"),
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
