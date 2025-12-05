from datetime import datetime
from bson import ObjectId
import json

class User:
    def __init__(self, data):
        self.id = str(data.get('_id', ObjectId()))
        self.username = data.get('username', '')
        self.email = data.get('email', '')
        self.role = data.get('role', 'student')  # student, teacher, admin
        self.created_at = data.get('created_at', datetime.utcnow())
        self.bookmarks = data.get('bookmarks', [])
        self.preferences = data.get('preferences', {})
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'bookmarks': self.bookmarks,
            'preferences': self.preferences
        }