from pathlib import Path
import fitz  # PyMuPDF
from docx import Document


def load_text_from_file(file_path: str) -> str:
    """
    Reads text from PDF, DOCX, or TXT files.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()

    if extension == ".pdf":
        return read_pdf(file_path)

    if extension == ".docx":
        return read_docx(file_path)

    if extension == ".txt":
        return read_txt(file_path)

    raise ValueError("Unsupported file type. Please use PDF, DOCX, or TXT.")


def read_pdf(file_path: str) -> str:
    text = ""

    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
            text += "\n"

    return clean_text(text)


def read_docx(file_path: str) -> str:
    document = Document(file_path)
    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return clean_text("\n".join(paragraphs))


def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return clean_text(file.read())


def clean_text(text: str) -> str:
    """
    Basic text cleaning.
    """
    text = text.replace("\x00", "")
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text