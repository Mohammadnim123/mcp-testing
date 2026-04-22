from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .tools import get_vector_store


async def ingest_data(file_path: str):
    """Ingest a PDF file into the local Chroma vector store."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(documents)

    store = get_vector_store()
    await store.aadd_documents(chunks)

    print(f"Ingested {len(chunks)} chunks from {file_path}")
