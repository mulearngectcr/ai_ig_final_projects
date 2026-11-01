from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.services.vector_store import store_recipe_text,get_uploaded_pdfs, delete_recipe_pdf
import fitz

router = APIRouter()

@router.get("/uploaded-pdfs")
async def list_uploaded_pdfs():
    return {"pdfs": get_uploaded_pdfs()}

@router.post("/upload")
async def upload_recipe_pdf(file: UploadFile = File(...)):

    # Check file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    try:
        # Read uploaded PDF
        pdf_bytes = await file.read()

        if not pdf_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty"
            )

        # Open PDF
        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        # Extract text from all pages
        text = ""

        for page in document:
            page_text = page.get_text()
            text += page_text + "\n"

        document.close()

        # Check whether text was extracted
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No extractable text found. Please upload a normal text-based PDF."
            )
        # Store extracted text in ChromaDB
        chunks_stored = store_recipe_text(
            file.filename,
            text
        )
        

        # Return extracted content
        return {
            "filename": file.filename,
            "text": text,
            "chunks_stored": chunks_stored,
            "message": "PDF uploaded and stored successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        await file.close()


@router.get("/files")
async def list_uploaded_pdfs():
    try:
        filenames = get_uploaded_pdfs()
        return {
            "total": len(filenames),
            "files": filenames
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{filename}")
def delete_uploaded_pdf(filename: str):
    try:
        delete_recipe_pdf(filename)

        return {
            "message": f"{filename} deleted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))