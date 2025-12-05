import requests
import json

def test_search(query):
    print(f"Testing search for: '{query}'")
    try:
        response = requests.post(
            'http://localhost:5000/api/search',
            json={'query': query, 'search_type': 'keyword'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search("dslab")
