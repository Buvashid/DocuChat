
from fastapi.testclient import TestClient
from unittest.mock import patch
from types import SimpleNamespace
from uuid import UUID

from app.main import app

client = TestClient(app)


@patch("app.routes.documents.add_document_chunks")
@patch("app.routes.documents.process_pdf_bytes")
def test_successful_pdf_upload(mock_process, mock_store):
    mock_process.return_value = [
        SimpleNamespace(page_number=1),
        SimpleNamespace(page_number=2),
    ]
    mock_store.return_value = ["chunk-1", "chunk-2"]

    response = client.post(
        "/documents/upload",
        files={"file": ("sample.pdf", b"fake-pdf-content", "application/pdf")},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample.pdf"
    assert data["pages_processed"] == 2
    assert data["chunks_created"] == 2

    document_id = data["document_id"]
    assert str(UUID(document_id)) == document_id

    mock_process.assert_called_once()
    assert mock_process.call_args.kwargs["document_id"] == document_id
    mock_store.assert_called_once()


@patch("app.routes.documents.add_document_chunks")
@patch("app.routes.documents.process_pdf_bytes")
def test_same_filename_uploads_get_unique_document_ids(mock_process, mock_store):
    mock_process.return_value = [
        SimpleNamespace(page_number=1),
    ]
    mock_store.return_value = ["chunk-1"]

    first_response = client.post(
        "/documents/upload",
        files={"file": ("sample.pdf", b"first-pdf-content", "application/pdf")},
    )

    second_response = client.post(
        "/documents/upload",
        files={"file": ("sample.pdf", b"second-pdf-content", "application/pdf")},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert first_data["filename"] == second_data["filename"]
    assert first_data["document_id"] != second_data["document_id"]

    first_id = mock_process.call_args_list[0].kwargs["document_id"]
    second_id = mock_process.call_args_list[1].kwargs["document_id"]

    assert first_id == first_data["document_id"]
    assert second_id == second_data["document_id"]

    assert mock_store.call_count == 2
