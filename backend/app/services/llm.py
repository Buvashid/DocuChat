from dataclasses import dataclass
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.services.retriever import (
	DEFAULT_RETRIEVAL_K,
	SourceReference,
	retrieve_relevant_context,
)
from langchain_chroma import Chroma


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
NOT_FOUND_MESSAGE = "The information was not found in the uploaded documents."

SYSTEM_PROMPT = f"""You answer questions using only the retrieved document context.
Do not use outside knowledge, assumptions, or information from the question itself.
If the answer is not explicitly supported by the context, reply exactly:
{NOT_FOUND_MESSAGE}
Keep the answer concise and accurate."""


class LLMConfigurationError(RuntimeError):
	"""Raised when Gemini cannot be configured from environment settings."""


@dataclass(frozen=True, slots=True)
class AnswerResult:
	"""An answer and the document locations used to produce it."""

	answer: str
	sources: tuple[SourceReference, ...]


@lru_cache(maxsize=4)
def get_gemini_client(
	model_name: str = DEFAULT_GEMINI_MODEL,
) -> ChatGoogleGenerativeAI:
	"""Return a cached Gemini client configured from environment settings."""

	api_key = get_settings().google_api_key
	if not api_key:
		raise LLMConfigurationError("GOOGLE_API_KEY is not configured")

	return ChatGoogleGenerativeAI(
		model=model_name,
		google_api_key=api_key,
		temperature=0,
	)


def answer_question(
	question: str,
	*,
	k: int = DEFAULT_RETRIEVAL_K,
	vector_store: Chroma | None = None,
	model_name: str = DEFAULT_GEMINI_MODEL,
) -> AnswerResult:
	"""Retrieve context and generate an answer grounded only in that context."""

	if not question.strip():
		raise ValueError("question must not be empty")

	retrieved = retrieve_relevant_context(question, k=k, vector_store=vector_store)
	if not retrieved.context:
		return AnswerResult(answer=NOT_FOUND_MESSAGE, sources=())

	response = get_gemini_client(model_name).invoke(
		[
			("system", SYSTEM_PROMPT),
			(
				"human",
				f"Retrieved document context:\n{retrieved.context}\n\n"
				f"Question:\n{question}",
			),
		]
	)
	answer = _response_text(response.content).strip()
	return AnswerResult(
		answer=answer or NOT_FOUND_MESSAGE,
		sources=retrieved.sources,
	)


def _response_text(content: object) -> str:
	if isinstance(content, str):
		return content
	if isinstance(content, list):
		return "".join(
			item.get("text", "")
			for item in content
			if isinstance(item, dict)
		)
	return str(content)
