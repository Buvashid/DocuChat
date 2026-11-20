
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.llm import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_id: str | None = None


class SourceReference(BaseModel):
    source: str
    page_number: int


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference]


def normalize_source(source) -> SourceReference:
    """Convert a source dictionary or object into a SourceReference."""

    if isinstance(source, dict):
        source_name = source.get("source", "")
        page_number = source.get("page_number", 0)
    else:
        source_name = getattr(source, "source", "")
        page_number = getattr(source, "page_number", 0)

    return SourceReference(
        source=str(source_name),
        page_number=int(page_number),
    )


@router.post("/", response_model=ChatResponse)
def chat_with_documents(request: ChatRequest):
    """Answer a question using the selected uploaded document."""

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question.",
        )

    try:
        result = answer_question(
            question,
            document_id=request.document_id,
        )

        sources = [
            normalize_source(source)
            for source in result["sources"]
        ]

        return ChatResponse(
            answer=result["answer"],
            sources=sources,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"Chat error: {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer. Please try again.",
        ) from error
