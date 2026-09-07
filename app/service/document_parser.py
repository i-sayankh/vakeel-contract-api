import os
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file

    Args:
        file_path (str): _description_

    Returns:
        str: _description_
    """
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return {
        "text": text.strip(),
        "page_count": len(reader.pages),
        "word_count": len(text.split()),
    }


def extract_text_from_txt(file_path: str) -> str:
    """Extracts text from a TXT file

    Args:
        file_path (str): _description_

    Returns:
        str: _description_
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return {
        "text": text.strip(),
        "page_count": 1,
        "word_count": len(text.split()),
    }


def extract_text(file_path: str) -> str:
    """Extracts text from a document file

    Args:
        file_path (str): _description_

    Returns:
        str: _description_
    """

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file type! Only PDF and TXT files are supported")
