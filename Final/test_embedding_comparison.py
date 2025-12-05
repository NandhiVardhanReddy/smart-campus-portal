from app.services.embedding_service import EmbeddingService
import numpy as np

def test_comparison():
    service = EmbeddingService()
    
    # Case 1: Identical content
    text1 = "This is a test document about machine learning."
    text2 = "This is a test document about machine learning."
    
    print(f"\nComparing identical texts:\nText 1: '{text1}'\nText 2: '{text2}'")
    emb1 = service.generate_embedding(text1)
    emb2 = service.generate_embedding(text2)
    
    if emb1 == emb2:
        print("Result: Embeddings are IDENTICAL.")
    else:
        print("Result: Embeddings are DIFFERENT.")
        
    # Case 2: Different content
    text3 = "This is a test document about baking cookies."
    
    print(f"\nComparing different texts:\nText 1: '{text1}'\nText 3: '{text3}'")
    emb3 = service.generate_embedding(text3)
    
    if emb1 == emb3:
        print("Result: Embeddings are IDENTICAL.")
    else:
        print("Result: Embeddings are DIFFERENT.")
        
    # Calculate similarity
    sim = service.calculate_similarity(emb1, emb3)
    print(f"\nSimilarity between Text 1 and Text 3: {sim:.4f}")

if __name__ == "__main__":
    test_comparison()
