from app.services.embedding_service import EmbeddingService

def test_embedding():
    print("Initializing EmbeddingService...")
    service = EmbeddingService()
    print("Generating embedding...")
    emb = service.generate_embedding("test query")
    print(f"Embedding generated. Length: {len(emb)}")

if __name__ == "__main__":
    test_embedding()
