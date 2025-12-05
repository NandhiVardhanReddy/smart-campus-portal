from flask import Blueprint, request, jsonify, current_app
from app.services.search_service import SearchService
from app.services.embedding_service import EmbeddingService
from app.models.document import Document

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
def search_documents():
    """Search documents with different search types"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'keyword')  # keyword, semantic, hybrid
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Initialize services
        embedding_service = EmbeddingService()
        search_service = SearchService(current_app.elasticsearch, embedding_service)
        
        # Build filters
        filters = {}
        if data.get('subject'):
            filters['subject'] = data['subject']
        if data.get('document_type'):
            filters['document_type'] = data['document_type']
        if data.get('author'):
            filters['author'] = data['author']
        
        # Perform search based on type
        if search_type == 'keyword':
            results = search_service.search_keyword(query, filters, page, page_size)
        elif search_type == 'semantic':
            results = search_service.search_semantic(query, filters, page, page_size)
        elif search_type == 'hybrid':
            results = search_service.search_hybrid(query, filters, page, page_size)
        else:
            return jsonify({'error': 'Invalid search type'}), 400

        # Fallback to MongoDB if Elasticsearch is down (results is None)
        if results is None:
            # Build MongoDB query
            mongo_query = {
                '$or': [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'content': {'$regex': query, '$options': 'i'}},
                    {'tags': {'$regex': query, '$options': 'i'}}
                ]
            }
            
            # Apply filters to MongoDB query
            if filters:
                if filters.get('subject'):
                    mongo_query['subject'] = filters['subject']
                if filters.get('document_type'):
                    mongo_query['document_type'] = filters['document_type']
                if filters.get('author'):
                    mongo_query['author'] = filters['author']
            
            # Execute MongoDB query
            cursor = current_app.db.documents.find(mongo_query).skip((page - 1) * page_size).limit(page_size)
            
            results = []
            for doc in cursor:
                try:
                    results.append({
                        'document': Document(doc).to_dict(),
                        'score': 1.0,
                        'search_type': 'fallback'
                    })
                except Exception:
                    pass

        return jsonify({
            'results': results,
            'query': query,
            'search_type': search_type,
            'page': page,
            'page_size': page_size,
            'total_results': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/search/suggest', methods=['GET'])
def search_suggest():
    """Get search suggestions"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'suggestions': []})
        
        # Get suggestions from Redis cache
        cache_key = f"suggestions:{query.lower()}"
        cached_suggestions = current_app.redis.get(cache_key)
        
        if cached_suggestions:
            return jsonify({'suggestions': eval(cached_suggestions)})
        
        # Generate suggestions (simplified - in production, use more sophisticated approach)
        suggestions = []
        
        # Get popular searches containing the query
        popular_searches = current_app.redis.zrevrange('popular_searches', 0, 9)
        for search in popular_searches:
            search_str = search.decode('utf-8') if isinstance(search, bytes) else search
            if query.lower() in search_str.lower():
                suggestions.append(search_str)
        
        # Get document titles containing the query
        documents = current_app.db.documents.find(
            {'title': {'$regex': query, '$options': 'i'}}
        ).limit(5)
        
        for doc in documents:
            suggestions.append(doc['title'])
        
        # Remove duplicates and limit
        suggestions = list(dict.fromkeys(suggestions))[:10]
        
        # Cache suggestions
        current_app.redis.setex(cache_key, 300, str(suggestions))  # Cache for 5 minutes
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/search/popular', methods=['GET'])
def popular_searches():
    """Get popular searches"""
    try:
        popular = current_app.redis.zrevrange('popular_searches', 0, 9, withscores=True)
        popular_searches = [
            {'query': search[0].decode('utf-8'), 'count': int(search[1])} 
            for search in popular
        ]
        
        return jsonify({'popular_searches': popular_searches})
    except Exception as e:
        return jsonify({'error': str(e)}), 500