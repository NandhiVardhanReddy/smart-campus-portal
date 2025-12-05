from elasticsearch import Elasticsearch
from app.services.embedding_service import EmbeddingService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, es_client, embedding_service):
        self.es = es_client
        self.embedding_service = embedding_service
        self.index_name = "documents"
        
    def create_index(self):
        """Create Elasticsearch index with mappings for both text and vector search"""
        try:
            if self.es.indices.exists(index=self.index_name):
                return True
                
            mapping = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "subject": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "document_type": {"type": "keyword"},
                        "author": {"type": "text"},
                        "uploaded_by": {"type": "keyword"},
                        "uploaded_at": {"type": "date"},
                        "likes": {"type": "integer"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 384  # Dimension for all-MiniLM-L6-v2
                        },
                        "metadata": {"type": "object"}
                    }
                }
            }
            
            self.es.indices.create(index=self.index_name, body=mapping, request_timeout=2)
            logger.info(f"Created Elasticsearch index: {self.index_name}")
            return True
        except Exception as e:
            try:
                logger.error(f"Error creating index: {str(e).encode('utf-8', 'ignore').decode('utf-8')}")
            except:
                logger.error("Error creating index (encoding failed)")
            return False
    
    def index_document(self, document):
        """Index a document in Elasticsearch"""
        try:
            doc_data = {
                "title": document.title,
                "content": document.content,
                "subject": document.subject,
                "tags": document.tags,
                "document_type": document.document_type,
                "author": document.author,
                "uploaded_by": document.uploaded_by,
                "uploaded_at": document.uploaded_at,
                "likes": document.likes,
                "embedding": document.embedding,
                "metadata": document.metadata
            }
            
            # Remove None values
            doc_data = {k: v for k, v in doc_data.items() if v is not None}
            
            self.es.index(index=self.index_name, id=document.id, body=doc_data, request_timeout=2)
            logger.info(f"Indexed document: {document.id}")
            return True
        except Exception as e:
            try:
                logger.error(f"Error indexing document: {str(e).encode('utf-8', 'ignore').decode('utf-8')}")
            except:
                logger.error("Error indexing document (encoding failed)")
            return False
    
    def search_keyword(self, query, filters=None, page=1, page_size=10):
        """Perform keyword search"""
        try:
            search_body = {
                "query": {
                    "bool": {
                        "must": {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content^2", "tags^2", "subject", "author"],
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                },
                "from": (page - 1) * page_size,
                "size": page_size,
                "highlight": {
                    "fields": {
                        "content": {},
                        "title": {}
                    }
                }
            }
            
            # Add filters
            if filters:
                filter_conditions = []
                if filters.get('subject'):
                    filter_conditions.append({"term": {"subject": filters['subject']}})
                if filters.get('document_type'):
                    filter_conditions.append({"term": {"document_type": filters['document_type']}})
                if filters.get('author'):
                    filter_conditions.append({"term": {"author": filters['author']}})
                
                if filter_conditions:
                    search_body["query"]["bool"]["filter"] = filter_conditions
            
            response = self.es.search(index=self.index_name, body=search_body, request_timeout=2)
            
            results = []
            for hit in response['hits']['hits']:
                doc = dict(hit['_source'])
                doc['id'] = hit['_id']
                result = {
                    'document': doc,
                    'score': hit['_score'],
                    'highlights': hit.get('highlight', {}),
                    'search_type': 'keyword'
                }
                results.append(result)
            
            return results
        except Exception as e:
            try:
                logger.error(f"Error in keyword search: {str(e).encode('utf-8', 'ignore').decode('utf-8')}")
            except:
                logger.error("Error in keyword search (encoding failed)")
            return None
    
    def search_semantic(self, query, filters=None, page=1, page_size=10):
        try:
            query_embedding = self.embedding_service.generate_embedding(query)
            if not query_embedding:
                return []

            search_body = {
                "knn": {
                    "field": "embedding",
                    "query_vector": query_embedding,
                    "k": page_size,
                    "num_candidates": 50
                }
            }

            # Add filters
            if filters:
                bool_filters = []
                if filters.get('subject'):
                    bool_filters.append({"term": {"subject": filters['subject']}})
                if filters.get('document_type'):
                    bool_filters.append({"term": {"document_type": filters['document_type']}})

                if bool_filters:
                    search_body["filter"] = bool_filters

            response = self.es.search(index=self.index_name, body=search_body, request_timeout=5)

            results = []
            for hit in response["hits"]["hits"]:
                # Filter by score threshold (adjust as needed, 0.6 is a reasonable starting point for cosine similarity)
                if hit["_score"] < 0.6:
                    continue

                doc = dict(hit["_source"])
                doc['id'] = hit['_id']
                results.append({
                    "document": doc,
                    "score": hit["_score"],
                    "search_type": "semantic"
                })

            return results

        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return None

    def search_hybrid(self, query, filters=None, page=1, page_size=10):
        """Perform hybrid search combining keyword and semantic"""
        try:
            # Get keyword results
            keyword_results = self.search_keyword(query, filters, page, page_size) or []
            
            # Get semantic results
            semantic_results = self.search_semantic(query, filters, page, page_size) or []
            
            # Combine and deduplicate results
            combined_results = []
            seen_ids = set()
            
            # Add semantic results first (they're typically more relevant)
            for result in semantic_results:
                doc_id = result['document'].get('id', '')
                if doc_id not in seen_ids:
                    combined_results.append(result)
                    seen_ids.add(doc_id)
            
            # Add keyword results that aren't already included
            for result in keyword_results:
                doc_id = result['document'].get('id', '')
                if doc_id not in seen_ids:
                    combined_results.append(result)
                    seen_ids.add(doc_id)
            
            # Sort by score and limit to page_size
            combined_results.sort(key=lambda x: x['score'], reverse=True)
            return combined_results[:page_size]
            
        except Exception as e:
            try:
                logger.error(f"Error in hybrid search: {str(e).encode('utf-8', 'ignore').decode('utf-8')}")
            except:
                logger.error("Error in hybrid search (encoding failed)")
            return None
    
    def delete_document(self, document_id):
        """Delete document from index"""
        try:
            self.es.delete(index=self.index_name, id=document_id, request_timeout=2)
            return True
        except Exception as e:
            try:
                logger.error(f"Error deleting document from index: {str(e).encode('utf-8', 'ignore').decode('utf-8')}")
            except:
                logger.error("Error deleting document (encoding failed)")
            return False