
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


@patch("app.routes.chat.answer_question")
def test_successful_chat(mock_answer):
    mock_answer.return_value = {
        "answer": "Maya Shah",
        "sources": [
            {
                "source": "sample.pdf",
                "page_number": 2,
            }
        ],
    }

    response = client.post(
        "/chat/",
        json={
            "question": "Who is the project coordinator?",
            "document_id": "doc-test-123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == "Maya Shah"
    assert data["sources"][0]["source"] == "sample.pdf"
    assert data["sources"][0]["page_number"] == 2

    mock_answer.assert_called_once_with(
        "Who is the project coordinator?",
        document_id="doc-test-123",
    )


def test_reject_empty_question():
    response = client.post(
        "/chat/",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_reject_whitespace_question():
    response = client.post(
        "/chat/",
        json={"question": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Please enter a question."


@patch("app.routes.chat.answer_question")
def test_chat_handles_llm_failure(mock_answer):
    mock_answer.side_effect = Exception("Gemini service unavailable")

    response = client.post(
        "/chat/",
        json={
            "question": "Who is the project coordinator?",
            "document_id": "doc-test-123",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Unable to generate an answer. Please try again."
    )
