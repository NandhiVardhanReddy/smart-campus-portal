import requests

BASE_URL = 'http://localhost:5000/api'

def cleanup():
    print("Cleaning up test documents...")
    # Find documents by title
    response = requests.get(f'{BASE_URL}/documents?page_size=100')
    if response.status_code != 200:
        print("Failed to fetch documents")
        return

    docs = response.json().get('documents', [])
    count = 0
    for doc in docs:
        if doc['title'] in ['Python Browser Test', 'Cooking Browser Test']:
            print(f"Deleting {doc['title']} ({doc['id']})...")
            requests.delete(f'{BASE_URL}/documents/{doc["id"]}')
            count += 1
    
    print(f"Deleted {count} documents.")

if __name__ == "__main__":
    cleanup()
