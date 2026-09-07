import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIRECTORY
from service.document_parser import extract_text

contracts_router = APIRouter(prefix="/contracts", tags=["Contracts"])


@contracts_router.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
):
    """
    Upload a PDF or TXT contract for analysis
    """

    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400, detail="File size too large! Max size is 5MB"
        )

    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{ext}"

    file_path = os.path.join(UPLOAD_DIRECTORY, unique_name)

    with open(file_path, "wb") as f:
        f.write(content)

    parsed = extract_text(file_path)

    return {"filename": file.filename}
