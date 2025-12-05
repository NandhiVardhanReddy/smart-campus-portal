from datetime import datetime
from bson import ObjectId
import json

class Document:
    def __init__(self, data):
        self.id = str(data.get('_id', ObjectId()))
        self.title = data.get('title', '')
        self.filename = data.get('filename', '')
        self.file_path = data.get('file_path', '')
        self.document_type = data.get('document_type', 'file')
from datetime import datetime
from bson import ObjectId
import json

class Document:
    def __init__(self, data):
        self.id = str(data.get('_id', ObjectId()))
        self.title = data.get('title', '')
        self.filename = data.get('filename', '')
        self.file_path = data.get('file_path', '')
        self.document_type = data.get('document_type', 'file')
        self.content = data.get('content', '')
        self.subject = data.get('subject', 'General')
        self.tags = data.get('tags', [])
        self.author = data.get('author', '')
        self.uploaded_by = data.get('uploaded_by', '')
        self.uploaded_at = data.get('uploaded_at', datetime.utcnow())
        self.likes = data.get('likes', 0)
        self.liked_by = data.get('liked_by', [])
        self.reviews = data.get('reviews', [])
        self.embedding = data.get('embedding', [])
        self.metadata = data.get('metadata', {})
        self.is_processed = data.get('is_processed', False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'filename': self.filename,
            'file_path': self.file_path,
            'document_type': self.document_type,
            'content': self.content,
            'subject': self.subject,
            'tags': self.tags,
            'author': self.author,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.isoformat() if isinstance(self.uploaded_at, datetime) else self.uploaded_at,
            'likes': self.likes,
            'liked_by': self.liked_by,
            'reviews': self.reviews,
            'metadata': self.metadata,
            'is_processed': self.is_processed
        }
    
    def to_json(self):
        return json.dumps(self.to_dict(), default=str)