import requests
import json

BASE_URL = "http://localhost:5000/api"

def list_and_test_like():
    try:
        # List docs
        r = requests.get(f"{BASE_URL}/documents")
        if r.status_code != 200:
            print(f"Failed to list docs: {r.status_code} {r.text}")
            return

        docs = r.json().get('documents', [])
        if not docs:
            print("No documents found.")
            return

        print(f"Found {len(docs)} documents.")
        doc = docs[0]
        doc_id = doc['id']
        print(f"Testing with document: {doc['title']} (ID: {doc_id})")

        # Test Like
        user_id = "test_user_123"
        print(f"Liking document {doc_id} as {user_id}...")
        r_like = requests.post(f"{BASE_URL}/documents/{doc_id}/like", json={"user_id": user_id})
        print(f"Like Status: {r_like.status_code}")
        print(f"Like Response: {r_like.text}")

        # Test Unlike
        print(f"Unliking document {doc_id} as {user_id}...")
        r_unlike = requests.post(f"{BASE_URL}/documents/{doc_id}/like", json={"user_id": user_id})
        print(f"Unlike Status: {r_unlike.status_code}")
        print(f"Unlike Response: {r_unlike.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_and_test_like()
