
import pytest

from app.services.document_processor import (
    DocumentProcessingError,
    process_pdf_bytes,
    _validate_chunk_settings,
)


def test_reject_zero_chunk_size():
    with pytest.raises(DocumentProcessingError):
        _validate_chunk_settings(0, 0)


def test_reject_negative_overlap():
    with pytest.raises(DocumentProcessingError):
        _validate_chunk_settings(1000, -1)


def test_reject_overlap_equal_to_chunk_size():
    with pytest.raises(DocumentProcessingError):
        _validate_chunk_settings(1000, 1000)


def test_reject_malformed_pdf():
    with pytest.raises(DocumentProcessingError):
        process_pdf_bytes(
            b"This is not a valid PDF",
            source="invalid.pdf",
        )


def test_empty_pdf_returns_no_chunks():
    from pypdf import PdfWriter
    from io import BytesIO

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    buffer = BytesIO()
    writer.write(buffer)

    chunks = process_pdf_bytes(
        buffer.getvalue(),
        source="blank.pdf",
    )

    assert chunks == []
