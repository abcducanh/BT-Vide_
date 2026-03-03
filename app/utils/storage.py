import os
from werkzeug.utils import secure_filename

ALLOWED_EXT = {"pdf", "zip", "rar", "docx", "xlsx", "pptx", "png", "jpg", "jpeg"}

def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXT

def save_upload(file_storage, upload_root: str, rel_dir: str) -> tuple[str, str, int]:
    """
    Returns: (relative_path, original_name, size)
    """
    original_name = file_storage.filename or "file"
    filename = secure_filename(original_name)

    abs_dir = os.path.join(upload_root, rel_dir)
    os.makedirs(abs_dir, exist_ok=True)

    abs_path = os.path.join(abs_dir, filename)
    file_storage.save(abs_path)
    size = os.path.getsize(abs_path)

    rel_path = os.path.join(rel_dir, filename)
    return rel_path, filename, size
