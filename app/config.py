from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

ALLOWED_EXTENSIONS = [".pdf", ".txt"]
MAX_FILE_SIZE_MB = 5
UPLOAD_DIRECTORY = "uploads"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
