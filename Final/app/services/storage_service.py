import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import PyPDF2
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
    
    def save_file(self, file, filename=None):
        """Save uploaded file and return file path"""
        try:
            if filename is None:
                filename = secure_filename(file.filename)
            
            # Generate unique filename
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            file.save(file_path)
            return file_path, unique_filename
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise
    
    def extract_text(self, file_path, file_type):
        """Extract text from different file types"""
        try:
            if file_type == 'pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_type in ['png', 'jpg', 'jpeg']:
                return self._extract_text_from_image(file_path)
            elif file_type in ['txt', 'md']:
                return self._extract_text_from_txt(file_path)
            else:
                return ""
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def _extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _extract_text_from_image(self, file_path):
        """Extract text from image using OCR"""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def _extract_text_from_txt(self, file_path):
        """Extract text from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from text file: {e}")
            return ""
    
    def delete_file(self, file_path):
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, file_path):
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime),
                'modified_at': datetime.fromtimestamp(stat.st_mtime)
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None