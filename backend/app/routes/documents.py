
import logging
import time
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_processor import (
    DocumentProcessingError,
    process_pdf_bytes,
)
from app.services.vector_store import add_document_chunks


router = APIRouter(prefix="/documents", tags=["documents"])

logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF with a unique document ID."""

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    upload_start = time.perf_counter()

    try:
        pdf_data = await file.read()

        if not pdf_data:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        document_id = str(uuid.uuid4())

        processing_start = time.perf_counter()

        chunks = process_pdf_bytes(
            pdf_data,
            source=file.filename,
            document_id=document_id,
        )

        logger.info(
            "PDF processing time: %.2f seconds; chunks: %d",
            time.perf_counter() - processing_start,
            len(chunks),
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No readable text was found in this PDF.",
            )

        storage_start = time.perf_counter()

        chunk_ids = add_document_chunks(chunks)

        logger.info(
            "Embedding and vector storage time: %.2f seconds; chunks stored: %d",
            time.perf_counter() - storage_start,
            len(chunk_ids),
        )

        logger.info(
            "Document uploaded: document_id=%s, filename=%s",
            document_id,
            file.filename,
        )

        return {
            "message": "Document uploaded successfully.",
            "document_id": document_id,
            "filename": file.filename,
            "pages_processed": len({chunk.page_number for chunk in chunks}),
            "chunks_created": len(chunk_ids),
        }

    except DocumentProcessingError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except HTTPException:
        raise

    except Exception as error:
        logger.exception("Failed to upload document")
        raise HTTPException(
            status_code=500,
            detail="Failed to save the document. Please try again.",
        ) from error

    finally:
        await file.close()
