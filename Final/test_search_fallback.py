import requests
import json

def test_search(query):
    print(f"Testing search for: '{query}'")
    try:
        response = requests.post(
            'http://localhost:5000/api/search',
            json={'query': query, 'search_type': 'semantic'},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"Total Results: {len(results)}")
            for res in results:
                doc = res.get('document', {})
                print(f" - Found: {doc.get('title')} (Type: {res.get('search_type')})")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_search("dslab")
    print("-" * 20)
    test_search("dbms")
