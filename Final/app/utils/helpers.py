import os
from datetime import datetime

def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = {'pdf', 'txt', 'md', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_file_hash(file_content):
    """Generate a hash for file content (simplified)"""
    import hashlib
    return hashlib.md5(file_content).hexdigest()

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def parse_date(date_string):
    """Parse date string to datetime object"""
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except:
        return datetime.utcnow()