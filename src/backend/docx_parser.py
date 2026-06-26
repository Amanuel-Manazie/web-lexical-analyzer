import io
from docx import Document

def extract_text_from_docx(file_obj):
    """
    Extract plain text from a .docx file.
    file_obj: A Flask FileStorage object (or any file-like object).
    Returns: A string containing all paragraph text, joined by newlines.
    """
    try:
        # Read the uploaded file into a BytesIO stream
        doc = Document(io.BytesIO(file_obj.read()))
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():  # Skip empty paragraphs
                full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        # If .docx is corrupted, raise a clear error
        raise ValueError(f"Could not parse .docx file: {str(e)}")