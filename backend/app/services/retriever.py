from dataclasses import dataclass
from collections.abc import Sequence

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.services.vector_store import similarity_search


DEFAULT_RETRIEVAL_K = 4


@dataclass(frozen=True, slots=True)
class SourceReference:
	"""Source location associated with retrieved context."""

	source: str
	page_number: int


@dataclass(frozen=True, slots=True)
class RetrievedContext:
	"""Retrieved documents, formatted context, and source references."""

	context: str
	documents: tuple[Document, ...]
	sources: tuple[SourceReference, ...]


def retrieve_relevant_context(
	question: str,
	*,
	k: int = DEFAULT_RETRIEVAL_K,
	vector_store: Chroma | None = None,
) -> RetrievedContext:
	"""Retrieve the most relevant chunks and build grounded LLM context."""

	if not question.strip():
		raise ValueError("question must not be empty")

	documents = tuple(
		document
		for document in similarity_search(question, k=k, vector_store=vector_store)
		if document.page_content.strip()
	)
	return RetrievedContext(
		context=build_context(documents),
		documents=documents,
		sources=_get_source_references(documents),
	)


def build_context(documents: Sequence[Document]) -> str:
	"""Format retrieved chunks with source and page markers for the LLM."""

	return "\n\n".join(
		f"[Source: {document.metadata.get('source', 'unknown')} | "
		f"Page: {document.metadata.get('page_number', 'unknown')}]\n"
		f"{document.page_content.strip()}"
		for document in documents
		if document.page_content.strip()
	)


def _get_source_references(
	documents: Sequence[Document],
) -> tuple[SourceReference, ...]:
	references: list[SourceReference] = []
	seen: set[tuple[str, int]] = set()

	for document in documents:
		source = str(document.metadata.get("source", "unknown"))
		page_value = document.metadata.get("page_number", 0)
		page_number = int(page_value) if str(page_value).isdigit() else 0
		reference = (source, page_number)
		if reference not in seen:
			seen.add(reference)
			references.append(
				SourceReference(source=source, page_number=page_number)
			)

	return tuple(references)
