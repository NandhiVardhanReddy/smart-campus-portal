from app import create_app
from app.services.search_service import SearchService
from app.services.embedding_service import EmbeddingService
from app.models.document import Document

def reindex_all():
    app = create_app()
    with app.app_context():
        print("Initializing services...")
        embedding_service = EmbeddingService()
        search_service = SearchService(app.elasticsearch, embedding_service)
        
        print("Creating index...")
        if search_service.create_index():
            print("Index created successfully.")
        else:
            print("Index creation failed (or already exists).")
            
        print("Fetching documents from MongoDB...")
        documents = list(app.db.documents.find({}))
        print(f"Found {len(documents)} documents.")
        
        success_count = 0
        for doc_data in documents:
            try:
                doc = Document(doc_data)
                if search_service.index_document(doc):
                    print(f"Indexed: {doc.title}")
                    success_count += 1
                else:
                    print(f"Failed to index: {doc.title}")
            except Exception as e:
                print(f"Error processing {doc_data.get('title')}: {e}")
                
        print(f"Re-indexing complete. Success: {success_count}/{len(documents)}")

if __name__ == "__main__":
    reindex_all()
