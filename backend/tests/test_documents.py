
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_reject_non_pdf_file():
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", b"Some text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload a PDF file."


def test_reject_empty_pdf():
    response = client.post(
        "/documents/upload",
        files={"file": ("empty.pdf", b"", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file is empty."
