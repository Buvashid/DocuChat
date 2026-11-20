
import logging
import time
import uuid

from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.services.document_processor import DocumentChunk
from app.services.embeddings import DEFAULT_EMBEDDING_MODEL, get_embedding_model


DEFAULT_COLLECTION_NAME = "docuchat_documents"
DEFAULT_PERSIST_DIRECTORY = Path(__file__).resolve().parents[2] / "chroma_db"

logger = logging.getLogger(__name__)


@lru_cache(maxsize=8)
def create_or_load_collection(
    persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> Chroma:
    """Create or reopen a persistent Chroma collection."""

    directory = Path(persist_directory)
    directory.mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embedding_model(embedding_model_name),
        persist_directory=str(directory),
    )


def add_document_chunks(
    chunks: Sequence[DocumentChunk],
    *,
    vector_store: Chroma | None = None,
    ids: Sequence[str] | None = None,
) -> list[str]:
    """Add document chunks using unique document and chunk IDs."""

    if not chunks:
        return []

    if ids is not None and len(ids) != len(chunks):
        raise ValueError("ids must contain one value per document chunk")

    document_ids = {
        chunk.document_id
        for chunk in chunks
        if chunk.document_id
    }

    if len(document_ids) > 1:
        raise ValueError("All chunks must belong to the same document")

    document_id = next(iter(document_ids), None) or str(uuid.uuid4())

    store = vector_store or create_or_load_collection()

    chunk_ids = list(ids) if ids is not None else [
        f"{document_id}:{chunk.page_number}:{chunk.chunk_index}"
        for chunk in chunks
    ]

    metadatas = [
        {
            **chunk.metadata,
            "document_id": document_id,
        }
        for chunk in chunks
    ]

    store.add_texts(
        texts=[chunk.text for chunk in chunks],
        metadatas=metadatas,
        ids=chunk_ids,
    )

    return chunk_ids


def similarity_search(
    query: str,
    *,
    k: int = 4,
    vector_store: Chroma | None = None,
    source: str | None = None,
    document_id: str | None = None,
) -> list[Document]:
    """Search relevant chunks, optionally filtered by document ID or source."""

    if not query.strip():
        raise ValueError("query must not be empty")

    if k <= 0:
        raise ValueError("k must be greater than zero")

    store = vector_store or create_or_load_collection()

    search_start = time.perf_counter()

    search_kwargs = {"k": k}

    filters = []

    if document_id:
        filters.append({"document_id": document_id})

    if source:
        filters.append({"source": source})

    if len(filters) == 1:
        search_kwargs["filter"] = filters[0]
    elif len(filters) > 1:
        search_kwargs["filter"] = {"$and": filters}

    results = store.similarity_search(query, **search_kwargs)

    logger.info(
        "Similarity search completed in %.2fs; document_id=%s; "
        "source=%s; results=%d",
        time.perf_counter() - search_start,
        document_id or "all documents",
        source or "all sources",
        len(results),
    )

    return results
