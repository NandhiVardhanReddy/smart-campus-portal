import requests
import time
import os

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

def test_search_relevance():
    print("1. Uploading test documents...")
    # Doc 1: Python
    id1 = upload_doc('python_test.txt', b'Python is a great programming language for data science and backend development.', 'Python Guide', 'Computer Science')
    
    # Doc 2: Cooking
    id2 = upload_doc('cooking_test.txt', b'To make a great cake, you need flour, sugar, eggs, and butter. Bake at 350 degrees.', 'Baking 101', 'Cooking')
    
    if not id1 or not id2:
        print("Failed to upload documents. Aborting.")
        return

    print("Documents uploaded. Waiting 2 seconds for indexing...")
    time.sleep(2)

    print("\n2. Searching for 'programming'...")
    response = requests.post(f'{BASE_URL}/search', json={'query': 'programming', 'search_type': 'hybrid'})
    results = response.json()
    print(f"DEBUG: Raw results type: {type(results)}")
    print(f"DEBUG: Raw results: {results}")
    
    if isinstance(results, dict) and 'error' in results:
        print(f"Search failed with error: {results['error']}")
        return

    if isinstance(results, dict) and 'results' in results:
        result_list = results['results']
    else:
        result_list = results # Fallback if it was a list

    found_python = False
    found_cooking = False

    print(f"Found {len(result_list)} results.")
    for res in result_list:
        doc_title = res['document']['title']
        score = res['score']
        print(f" - {doc_title} (Score: {score})")
        
        if res['document']['title'] == 'Python Guide':
            found_python = True
        if res['document']['title'] == 'Baking 101':
            found_cooking = True

    print("\n3. Verifying results...")
    if found_python:
        print("[PASS] 'Python Guide' was found.")
    else:
        print("[FAIL] 'Python Guide' was NOT found.")

    if not found_cooking:
        print("[PASS] 'Baking 101' was NOT found (Correct).")
    else:
        print("[FAIL] 'Baking 101' WAS found (Incorrect, unless fuzzy match).")

    # Cleanup
    print("\n4. Cleaning up...")
    delete_doc(id1)
    delete_doc(id2)
    print("Done.")

if __name__ == "__main__":
    try:
        test_search_relevance()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the server is running on localhost:5000")
