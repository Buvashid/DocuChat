
from unittest.mock import MagicMock
from uuid import UUID

from app.services.document_processor import DocumentChunk
from app.services.vector_store import add_document_chunks, similarity_search


def test_add_document_chunks_stores_document_id():
    mock_store = MagicMock()

    chunk = DocumentChunk(
        text="First document content",
        source="sample.pdf",
        page_number=1,
        chunk_index=0,
        document_id="doc-123",
    )

    chunk_ids = add_document_chunks(
        [chunk],
        vector_store=mock_store,
    )

    assert chunk_ids == ["doc-123:1:0"]

    mock_store.add_texts.assert_called_once()

    call_kwargs = mock_store.add_texts.call_args.kwargs

    assert call_kwargs["metadatas"][0]["document_id"] == "doc-123"
    assert call_kwargs["texts"] == ["First document content"]


def test_similarity_search_filters_by_document_id():
    mock_store = MagicMock()
    mock_store.similarity_search.return_value = []

    similarity_search(
        "What is this document about?",
        k=4,
        vector_store=mock_store,
        document_id="doc-123",
    )

    mock_store.similarity_search.assert_called_once_with(
        "What is this document about?",
        k=4,
        filter={"document_id": "doc-123"},
    )


def test_similarity_search_filters_by_document_id_and_filename():
    mock_store = MagicMock()
    mock_store.similarity_search.return_value = []

    similarity_search(
        "Project details",
        vector_store=mock_store,
        source="sample.pdf",
        document_id="doc-123",
    )

    mock_store.similarity_search.assert_called_once_with(
        "Project details",
        k=4,
        filter={
            "$and": [
                {"document_id": "doc-123"},
                {"source": "sample.pdf"},
            ]
        },
    )
