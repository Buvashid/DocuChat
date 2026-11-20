
import hashlib

from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma

from app.services.document_processor import DocumentChunk
from app.services.vector_store import add_document_chunks, similarity_search


class TestEmbeddings(Embeddings):
    """Deterministic embeddings for isolated Chroma integration tests."""

    def _vector(self, text):
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [value / 255.0 for value in digest[:16]]

    def embed_documents(self, texts):
        return [self._vector(text) for text in texts]

    def embed_query(self, text):
        return self._vector(text)


def test_chroma_isolates_documents_with_same_filename(tmp_path):
    store = Chroma(
        collection_name="docuchat_integration_test",
        embedding_function=TestEmbeddings(),
        persist_directory=str(tmp_path),
    )

    first_chunk = DocumentChunk(
        text="The first document coordinator is Maya Shah.",
        source="sample.pdf",
        page_number=1,
        chunk_index=0,
        document_id="document-A",
    )

    second_chunk = DocumentChunk(
        text="The second document coordinator is Rahul Patil.",
        source="sample.pdf",
        page_number=1,
        chunk_index=0,
        document_id="document-B",
    )

    add_document_chunks([first_chunk], vector_store=store)
    add_document_chunks([second_chunk], vector_store=store)

    first_results = similarity_search(
        "Who is the coordinator?",
        k=5,
        vector_store=store,
        source="sample.pdf",
        document_id="document-A",
    )

    second_results = similarity_search(
        "Who is the coordinator?",
        k=5,
        vector_store=store,
        source="sample.pdf",
        document_id="document-B",
    )

    assert len(first_results) == 1
    assert len(second_results) == 1

    assert "Maya Shah" in first_results[0].page_content
    assert "Rahul Patil" in second_results[0].page_content

    assert first_results[0].metadata["document_id"] == "document-A"
    assert second_results[0].metadata["document_id"] == "document-B"
