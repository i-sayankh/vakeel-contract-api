import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, UPLOAD_DIRECTORY
from service.document_parser import extract_text
from models import Contract
from database import contracts_collection

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

    contract_data = Contract(
        filename=unique_name,
        original_name=file.filename,
        text_content=parsed["text"] if isinstance(parsed, dict) else parsed,
        page_count=(
            int(parsed["page_count"])
            if isinstance(parsed, dict)
            else len(parsed.splitlines())
        ),
        word_count=(
            int(parsed["word_count"])
            if isinstance(parsed, dict)
            else len(parsed.split())
        ),
    )

    doc = contract_data.model_dump()
    result = contracts_collection.insert_one(doc)
    contract_data.id = str(result.inserted_id)

    return {
        "message": "File uploaded and parsed successfully",
        "contract": contract_data.model_dump(),
        "id": contract_data.id,
    }
