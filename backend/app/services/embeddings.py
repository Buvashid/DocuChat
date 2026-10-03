from functools import lru_cache
from collections.abc import Sequence

from langchain_huggingface import HuggingFaceEmbeddings


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=4)
def get_embedding_model(
	model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> HuggingFaceEmbeddings:
	"""Return a cached HuggingFace embedding model."""

	return HuggingFaceEmbeddings(
		model_name=model_name,
		encode_kwargs={"normalize_embeddings": True},
	)


def generate_embeddings(
	texts: Sequence[str],
	*,
	model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[list[float]]:
	"""Generate normalized embeddings for document texts."""

	if not texts:
		return []
	if any(not text.strip() for text in texts):
		raise ValueError("texts must not contain empty values")

	return get_embedding_model(model_name).embed_documents(list(texts))


def generate_query_embedding(
	query: str,
	*,
	model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[float]:
	"""Generate a normalized embedding for a search query."""

	if not query.strip():
		raise ValueError("query must not be empty")

	return get_embedding_model(model_name).embed_query(query)
