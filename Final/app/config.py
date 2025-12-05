import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # File upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Database configurations
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/smart_library')
    MONGODB_DB_NAME = 'smart_library'
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Elasticsearch configuration
import os
from datetime import timedelta

class Config:
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # File upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Database configurations
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/smart_library')
    MONGODB_DB_NAME = 'smart_library'
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Elasticsearch configuration
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://127.0.0.1:9200')
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Model configurations
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    SIMILARITY_THRESHOLD = 0.7