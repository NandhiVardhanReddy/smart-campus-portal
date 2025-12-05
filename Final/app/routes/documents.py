from flask import Blueprint, request, jsonify, current_app, send_file
from bson import ObjectId
from datetime import datetime
import os
from app.models.document import Document
from app.services.storage_service import StorageService
from app.services.embedding_service import EmbeddingService
from app.services.search_service import SearchService
from app.utils.helpers import allowed_file
import traceback

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@documents_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get all documents with pagination and filtering"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        subject = request.args.get('subject')
        doc_type = request.args.get('type')
        
        query = {}
        if subject:
            query['subject'] = subject
        if doc_type:
            query['document_type'] = doc_type
        
        skip = (page - 1) * page_size
        
        # Get total count
        total = current_app.db.documents.count_documents(query)
        
        # Get documents
        cursor = current_app.db.documents.find(query).sort('uploaded_at', -1).skip(skip).limit(page_size)
        documents = [Document(doc).to_dict() for doc in cursor]
        
        return jsonify({
            'documents': documents,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document"""
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({'error': 'Invalid document ID'}), 400

        document = current_app.db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({'document': Document(document).to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({'error': 'Invalid document ID'}), 400

        # Find document to get file path
        doc = current_app.db.documents.find_one({'_id': ObjectId(document_id)})
        if not doc:
            return jsonify({'error': 'Document not found'}), 404

        # Delete from MongoDB
        current_app.db.documents.delete_one({'_id': ObjectId(document_id)})

        # Initialize services
        storage_service = StorageService(current_app.config['UPLOAD_FOLDER'])
        # Embedding service not needed for delete, passing None
        search_service = SearchService(current_app.elasticsearch, None)

        # Delete from Elasticsearch
        search_service.delete_document(document_id)

        # Delete file from storage
        if 'file_path' in doc:
            storage_service.delete_file(doc['file_path'])

        return jsonify({'message': 'Document deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download a document file"""
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({'error': 'Invalid document ID'}), 400

        doc = current_app.db.documents.find_one({'_id': ObjectId(document_id)})
        if not doc:
            return jsonify({'error': 'Document not found'}), 404
            
        file_path = doc.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=doc.get('title', 'download') + (os.path.splitext(doc.get('filename', ''))[1] if doc.get('filename') else '')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents', methods=['POST'])
def upload_document():
    try:
        # Check file
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # Form fields

        title = request.form.get('title')
        if not title:
            title = os.path.splitext(file.filename)[0]
        subject = request.form.get('subject', 'General')
        document_type = request.form.get('document_type', 'file')
        author = request.form.get('author', 'Teacher')

        # Services
        storage_service = StorageService(current_app.config['UPLOAD_FOLDER'])
        embedding_service = EmbeddingService()
        search_service = SearchService(current_app.elasticsearch, embedding_service)

        # Save file
        file_path, filename = storage_service.save_file(file)

        # Extract text
        file_ext = os.path.splitext(filename)[1][1:].lower()
        content = storage_service.extract_text(file_path, file_ext) or ""

        # Auto keywords
        tags = embedding_service.extract_keywords(content, 5) if content else []

        # Build rich embedding text
        summary = embedding_service.summarize_text(content, max_length=300)
        tags_text = " ".join(tags)

        combined_text = " ".join([
            title,
            content[:800],   # first chunk of content
            summary,
            tags_text
        ])

        combined_text = combined_text.strip() or title

        # Generate powerful embedding
        embedding = embedding_service.generate_embedding(combined_text)

        document_data = {
            'title': title,
            'filename': filename,
            'file_path': file_path,
            'document_type': document_type,
            'content': content,
            'subject': subject,
            'tags': tags,
            'author': author,
            'uploaded_by': author,
            'uploaded_at': datetime.utcnow(),
            'likes': 0,
            'reviews': [],
            'embedding': embedding,
            'metadata': {
                'file_size': os.path.getsize(file_path),
                'word_count': len(content.split())
            },
            'is_processed': True
        }

        # Insert Mongo
        result = current_app.db.documents.insert_one(document_data)
        document_data["_id"] = result.inserted_id

        # Index in Elasticsearch
        try:
            search_service.index_document(Document(document_data))
        except Exception as es_err:
            print("ES indexing failed:", es_err)

        return jsonify({
            'message': 'Document uploaded successfully',
            'document': Document(document_data).to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents/<document_id>/review', methods=['POST'])
def add_review(document_id):
    """Add a review to a document"""
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({'error': 'Invalid document ID'}), 400

        data = request.get_json()
        review_text = data.get('text', '')
        rating = data.get('rating', 5)
        author = data.get('author', 'Anonymous')
        
        if not review_text:
            return jsonify({'error': 'Review text is required'}), 400
        
        review = {
            'id': str(ObjectId()),
            'text': review_text,
            'rating': rating,
            'author': author,
            'date': datetime.utcnow()
        }
        
        result = current_app.db.documents.update_one(
            {'_id': ObjectId(document_id)},
            {'$push': {'reviews': review}}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({'message': 'Review added successfully', 'review': review})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/documents/<document_id>/like', methods=['POST'])
def like_document(document_id):
    """Like or unlike a document"""
    try:
        if not ObjectId.is_valid(document_id):
            return jsonify({'error': 'Invalid document ID'}), 400

        data = request.get_json() or {}
        user_id = data.get('user_id')

        # Find the document first to check current state
        doc = current_app.db.documents.find_one({'_id': ObjectId(document_id)})
        if not doc:
            return jsonify({'error': 'Document not found'}), 404

        liked_by = doc.get('liked_by', [])
        current_likes = doc.get('likes', 0)

        if user_id and user_id in liked_by:
            # Unlike
            new_likes = max(0, current_likes - 1)
            update_op = {
                '$set': {'likes': new_likes},
                '$pull': {'liked_by': user_id}
            }
            liked = False
        else:
            # Like
            new_likes = current_likes + 1
            update_op = {
                '$set': {'likes': new_likes}
            }
            if user_id:
                update_op['$push'] = {'liked_by': user_id}
            liked = True

        current_app.db.documents.update_one(
            {'_id': ObjectId(document_id)},
            update_op
        )
        
        return jsonify({
            'message': 'Document like status updated',
            'likes': new_likes,
            'liked': liked
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500