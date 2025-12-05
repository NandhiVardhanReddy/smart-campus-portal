import requests
import time

BASE_URL = 'http://localhost:5000/api'

def upload_doc(filename, content, title, subject):
    files = {'file': (filename, content)}
    data = {'title': title, 'subject': subject, 'document_type': 'note'}
    response = requests.post(f'{BASE_URL}/documents', files=files, data=data)
    if response.status_code == 201:
        return response.json()['document']['id']
    else:
        print(f"Failed to upload {filename}: {response.text}")
        return None

def delete_doc(doc_id):
    requests.delete(f'{BASE_URL}/documents/{doc_id}')

def test_semantic_search():
    print("1. Uploading test document...")
    # Content has NO shared words with query "fast animal"
    # "quick" ~= "fast", "fox" ~= "animal"
    content = b'The quick brown fox jumps over the lazy dog.'
    doc_id = upload_doc('semantic_test.txt', content, 'Fox Story', 'General')
    
    if not doc_id:
        print("Upload failed.")
        return

    print("Document uploaded. Waiting 2 seconds for indexing...")
    time.sleep(2)

    query = "fast animal"
    print(f"\n2. Testing Query: '{query}'")

    # Test 1: Keyword Search (Should FAIL)
    print("\n--- Keyword Search ---")
    resp_kw = requests.post(f'{BASE_URL}/search', json={'query': query, 'search_type': 'keyword'})
    results_kw = resp_kw.json().get('results', [])
    print(f"Found {len(results_kw)} results.")
    
    keyword_success = len(results_kw) == 0
    if keyword_success:
        print("[PASS] Keyword search found NOTHING (Expected, as there are no shared words).")
    else:
        print(f"[FAIL] Keyword search found {len(results_kw)} results (Unexpected).")

    # Test 2: Semantic Search (Should PASS)
    print("\n--- Semantic Search ---")
    resp_sem = requests.post(f'{BASE_URL}/search', json={'query': query, 'search_type': 'semantic'})
    results_sem = resp_sem.json().get('results', [])
    print(f"Found {len(results_sem)} results.")
    
    semantic_success = False
    for res in results_sem:
        print(f" - {res['document']['title']} (Score: {res['score']})")
        if res['document']['title'] == 'Fox Story':
            semantic_success = True

    if semantic_success:
        print("[PASS] Semantic search FOUND the document (Expected).")
    else:
        print("[FAIL] Semantic search did NOT find the document.")

    # Cleanup
    print("\n3. Cleaning up...")
    delete_doc(doc_id)
    print("Done.")

if __name__ == "__main__":
    try:
        test_semantic_search()
    except Exception as e:
        print(f"Error: {e}")
