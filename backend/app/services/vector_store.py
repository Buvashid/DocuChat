from functools import lru_cache
from pathlib import Path
from collections.abc import Sequence

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.services.document_processor import DocumentChunk
from app.services.embeddings import DEFAULT_EMBEDDING_MODEL, get_embedding_model


DEFAULT_COLLECTION_NAME = "docuchat_documents"
DEFAULT_PERSIST_DIRECTORY = Path(__file__).resolve().parents[2] / "chroma_db"


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
	"""Add document chunks and metadata to the Chroma collection."""

	if not chunks:
		return []
	if ids is not None and len(ids) != len(chunks):
		raise ValueError("ids must contain one value per document chunk")

	store = vector_store or create_or_load_collection()
	chunk_ids = list(ids) if ids is not None else [
		f"{chunk.source}:{chunk.page_number}:{chunk.chunk_index}"
		for chunk in chunks
	]
	store.add_texts(
		texts=[chunk.text for chunk in chunks],
		metadatas=[chunk.metadata for chunk in chunks],
		ids=chunk_ids,
	)
	return chunk_ids


def similarity_search(
	query: str,
	*,
	k: int = 4,
	vector_store: Chroma | None = None,
) -> list[Document]:
	"""Return the most similar document chunks for a query."""

	if not query.strip():
		raise ValueError("query must not be empty")
	if k <= 0:
		raise ValueError("k must be greater than zero")

	store = vector_store or create_or_load_collection()
	return store.similarity_search(query, k=k)
