import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings


async def ingest_data(file_path: str):
    """Ingest a PDF file into Pinecone vector store."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(documents)

    embeddings = PineconeEmbeddings(model="llama-text-embed-v2")
    store = PineconeVectorStore.from_existing_index(
        index_name=os.environ["PINECONE_INDEX"],
        embedding=embeddings,
    )

    batch_size = 96
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        await store.aadd_documents(batch)

    print(f"Ingested {len(chunks)} chunks from {file_path}")
