from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


DEFAULT_CHUNK_SIZE = 1_000
DEFAULT_CHUNK_OVERLAP = 200


class DocumentProcessingError(Exception):
	"""Raised when a PDF cannot be read or processed."""


@dataclass(frozen=True, slots=True)
class DocumentChunk:
	"""A searchable text chunk and its source location."""

	text: str
	source: str
	page_number: int
	chunk_index: int

	@property
	def metadata(self) -> dict[str, str | int]:
		"""Return metadata in the shape expected by vector-store clients."""

		return {
			"source": self.source,
			"page_number": self.page_number,
			"chunk_index": self.chunk_index,
		}


def process_pdf(
	file_path: str | Path,
	*,
	chunk_size: int = DEFAULT_CHUNK_SIZE,
	chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
	"""Extract and chunk a PDF file while preserving page metadata."""

	path = Path(file_path)
	try:
		with path.open("rb") as pdf_file:
			return process_pdf_stream(
				pdf_file,
				source=path.name,
				chunk_size=chunk_size,
				chunk_overlap=chunk_overlap,
			)
		
	except OSError as error:
		raise DocumentProcessingError(f"Unable to read PDF '{path}': {error}") from error


def process_pdf_bytes(
	pdf_data: bytes,
	*,
	source: str = "uploaded.pdf",
	chunk_size: int = DEFAULT_CHUNK_SIZE,
	chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
	"""Extract and chunk PDF bytes, preserving the supplied source name."""

	return process_pdf_stream(
		BytesIO(pdf_data),
		source=source,
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap,
	)


def process_pdf_stream(
	pdf_stream: BinaryIO,
	*,
	source: str,
	chunk_size: int = DEFAULT_CHUNK_SIZE,
	chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
	"""Extract and chunk a readable binary PDF stream."""

	_validate_chunk_settings(chunk_size, chunk_overlap)

	try:
		reader = PdfReader(pdf_stream)
		text_splitter = RecursiveCharacterTextSplitter(
			chunk_size=chunk_size,
			chunk_overlap=chunk_overlap,
			separators=["\n\n", "\n", " ", ""],
		)
		chunks: list[DocumentChunk] = []

		for page_number, page in enumerate(reader.pages, start=1):
			page_text = (page.extract_text() or "").strip()
			if not page_text:
				continue

			for text in text_splitter.split_text(page_text):
				chunks.append(
					DocumentChunk(
						text=text,
						source=source,
						page_number=page_number,
						chunk_index=len(chunks),
					)
				)
		
		return chunks
	except Exception as error:
		if isinstance(error, DocumentProcessingError):
			raise
		raise DocumentProcessingError(
			f"Unable to process PDF '{source}': {error}"
		) from error


def _validate_chunk_settings(chunk_size: int, chunk_overlap: int) -> None:
	if chunk_size <= 0:
		raise DocumentProcessingError("chunk_size must be greater than zero")
	if chunk_overlap < 0:
		raise DocumentProcessingError("chunk_overlap cannot be negative")
	if chunk_overlap >= chunk_size:
		raise DocumentProcessingError("chunk_overlap must be smaller than chunk_size")
