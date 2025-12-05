import requests
import json
import time

BASE_URL = 'http://localhost:5000/api'

def test_semantic_search():
    print("Testing Semantic Search (Live Server)...")
    
    search_data = {
        'query': 'neural networks',
        'search_type': 'semantic',
        'page': 1,
        'page_size': 10
    }
    
    try:
        start_time = time.time()
        response = requests.post(f'{BASE_URL}/search', json=search_data)
        end_time = time.time()
        
        print(f"Status Code: {response.status_code}")
        print(f"Time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2)[:500] + "...")
        else:
            print("Error:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("Connection Error: The server might be down or not running on port 5000.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_semantic_search()
