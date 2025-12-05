from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        # Document statistics
        total_documents = current_app.db.documents.count_documents({})
        documents_by_subject = list(current_app.db.documents.aggregate([
            {'$group': {'_id': '$subject', 'count': {'$sum': 1}}}
        ]))
        documents_by_type = list(current_app.db.documents.aggregate([
            {'$group': {'_id': '$document_type', 'count': {'$sum': 1}}}
        ]))
        
        # Search statistics
        total_searches = current_app.redis.get('total_searches') or 0
        total_searches = int(total_searches)
        
        # Storage statistics
        storage_stats = current_app.db.command('dbStats')
        
        return jsonify({
            'documents': {
                'total': total_documents,
                'by_subject': documents_by_subject,
                'by_type': documents_by_type
            },
            'searches': {
                'total': total_searches
            },
            'storage': {
                'data_size': storage_stats.get('dataSize', 0),
                'storage_size': storage_stats.get('storageSize', 0)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/reindex-all', methods=['POST'])
def reindex_all():
    """Reindex all documents in Elasticsearch"""
    try:
        from app.services.search_service import SearchService
        from app.services.embedding_service import EmbeddingService
        from app.models.document import Document
        
        embedding_service = EmbeddingService()
        search_service = SearchService(current_app.elasticsearch, embedding_service)
        
        # Create index if it doesn't exist
        search_service.create_index()
        
        # Get all documents
        documents = current_app.db.documents.find()
        
        reindexed_count = 0
        for doc_data in documents:
            document = Document(doc_data)
            if search_service.index_document(document):
                reindexed_count += 1
        
        return jsonify({
            'message': f'Successfully reindexed {reindexed_count} documents',
            'successfully_indexed': reindexed_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/cache/clear', methods=['POST'])
def clear_cache():
    """Clear Redis cache"""
    try:
        current_app.redis.flushdb()
        return jsonify({'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/reset', methods=['POST'])
def reset_system():
    """Reset the entire system: clear DB, ES, Redis, and files"""
    try:
        # 1. Clear MongoDB
        current_app.db.documents.delete_many({})
        
        # 2. Clear Elasticsearch
        try:
            current_app.elasticsearch.indices.delete(index='documents', ignore=[400, 404])
            # Recreate empty index
            from app.services.search_service import SearchService
            from app.services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService()
            search_service = SearchService(current_app.elasticsearch, embedding_service)
            search_service.create_index()
        except Exception as es_e:
            print(f"ES clear warning: {es_e}")

        # 3. Clear Redis
        try:
            current_app.redis.flushdb()
        except Exception as r_e:
            print(f"Redis clear warning: {r_e}")

        # 4. Clear Uploads Folder
        import os
        import shutil
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_folder):
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

        return jsonify({'message': 'System reset successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/debug/status', methods=['GET'])
def debug_status():
    """Debug endpoint to check service status"""
    try:
        # Check MongoDB
        mongo_status = 'connected' if current_app.db.command('ping') else 'disconnected'
        
        # Check Redis
        try:
            current_app.redis.ping()
            redis_status = 'connected'
        except:
            redis_status = 'disconnected'
        
        # Check Elasticsearch
        try:
            es_info = current_app.elasticsearch.info()
            elasticsearch_status = 'connected'
        except:
            elasticsearch_status = 'disconnected'
        
        return jsonify({
            'services': {
                'mongodb': mongo_status,
                'redis': redis_status,
                'elasticsearch': elasticsearch_status
            },
            'document_count': current_app.db.documents.count_documents({}),
            'index_exists': current_app.elasticsearch.indices.exists(index='documents')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500