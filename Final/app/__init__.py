from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import redis
from elasticsearch import Elasticsearch

import os

# Initialize extensions
cors = CORS()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object('Final.app.config.Config')
    
    # Initialize extensions
    cors.init_app(app)
    jwt.init_app(app)
    
    # Initialize database connections
    app.mongo = MongoClient(app.config['MONGODB_URI'])
    app.db = app.mongo[app.config['MONGODB_DB_NAME']]
    
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Elasticsearch initialization
    es_params = {
        'verify_certs': True,
        'request_timeout': 30,
        'max_retries': 3,
        'retry_on_timeout': True
    }
    
    if app.config.get('ELASTIC_CLOUD_ID'):
        es_params['cloud_id'] = app.config['ELASTIC_CLOUD_ID']
        es_params['api_key'] = app.config['ELASTIC_API_KEY']
    else:
        es_params['hosts'] = [app.config['ELASTICSEARCH_URL']]
        es_params['verify_certs'] = False # Local development
        
    app.elasticsearch = Elasticsearch(**es_params)
    
    # Register blueprints
    from Final.app.routes.documents import documents_bp
    from Final.app.routes.search import search_bp
    from Final.app.routes.admin import admin_bp
    
    app.register_blueprint(documents_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import redis
from elasticsearch import Elasticsearch

import os

# Initialize extensions
cors = CORS()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object('Final.app.config.Config')
    
    # Initialize extensions
    cors.init_app(app)
    jwt.init_app(app)
    
    # Initialize database connections
    app.mongo = MongoClient(app.config['MONGODB_URI'])
    app.db = app.mongo[app.config['MONGODB_DB_NAME']]
    
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Elasticsearch initialization
    es_params = {
        'verify_certs': True,
        'request_timeout': 30,
        'max_retries': 3,
        'retry_on_timeout': True
    }
    
    if app.config.get('ELASTIC_CLOUD_ID'):
        es_params['cloud_id'] = app.config['ELASTIC_CLOUD_ID']
        es_params['api_key'] = app.config['ELASTIC_API_KEY']
    else:
        es_params['hosts'] = [app.config['ELASTICSEARCH_URL']]
        es_params['verify_certs'] = False # Local development
        
    app.elasticsearch = Elasticsearch(**es_params)
    
    # Register blueprints
    from Final.app.routes.documents import documents_bp
    from Final.app.routes.search import search_bp
    from Final.app.routes.admin import admin_bp
    
    app.register_blueprint(documents_bp, url_prefix='/api')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    

    return app

