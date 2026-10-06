# app/utils/file_storage.py
import os
import secrets
from werkzeug.utils import secure_filename
from datetime import datetime

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder(category="general", subfolder=""):
    """Get or create upload folder path"""
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
    
    if category == "company_docs":
        path = os.path.join(base_path, 'company_docs', subfolder)
    elif category == "resumes":
        path = os.path.join(base_path, 'resumes')
    elif category == "linkedin_pdfs":
        path = os.path.join(base_path, 'linkedin_pdfs')
    elif category == "chat_files":
        path = os.path.join(base_path, 'chat_files')
    else:
        path = os.path.join(base_path, category)
    
    os.makedirs(path, exist_ok=True)
    return path


def save_upload_file(file_obj, category="general", subfolder="", user_id=None):
    """
    Save uploaded file securely
    
    Args:
        file_obj: FileStorage object from Flask
        category: Category of upload (company_docs, resumes, etc.)
        subfolder: Additional subfolder within category
        user_id: Optional user ID to organize files
    
    Returns:
        Relative file path or full filename
    """
    if not file_obj or file_obj.filename == '':
        return None
    
    filename = secure_filename(file_obj.filename)
    if not allowed_file(filename):
        raise ValueError(f"File type not allowed: {filename}")
    
    # Check file size
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size / (1024*1024):.2f}MB exceeds {MAX_FILE_SIZE / (1024*1024):.0f}MB limit")
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    random_suffix = secrets.token_hex(6)
    file_ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{timestamp}_{random_suffix}.{file_ext}"
    
    # Create path
    if category == "company_docs" and subfolder:
        folder = get_upload_folder(category, subfolder)
        relative_path = f"company_docs/{subfolder}/{new_filename}"
    elif user_id:
        folder = get_upload_folder(category, str(user_id))
        relative_path = f"{category}/{user_id}/{new_filename}"
    else:
        folder = get_upload_folder(category, subfolder)
        relative_path = f"{category}/{subfolder}/{new_filename}" if subfolder else f"{category}/{new_filename}"
    
    # Save file
    full_path = os.path.join(folder, new_filename)
    file_obj.save(full_path)
    
    return relative_path


def get_file_path(relative_path):
    """Get full file path from relative path"""
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
    return os.path.join(base_path, relative_path)


def delete_file(relative_path):
    """Delete a file"""
    full_path = get_file_path(relative_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False
