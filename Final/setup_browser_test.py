import requests
import time

BASE_URL = 'http://localhost:5000/api'

def upload_doc(filename, content, title, subject):
    files = {'file': (filename, content)}
    data = {'title': title, 'subject': subject, 'document_type': 'note'}
    response = requests.post(f'{BASE_URL}/documents', files=files, data=data)
    if response.status_code == 201:
        print(f"Uploaded: {title}")
        return response.json()['document']['id']
    else:
        print(f"Failed to upload {filename}: {response.text}")
        return None

def setup():
    print("Uploading test documents...")
    # Doc 1: Python
    upload_doc('python_test.txt', b'Python is a great programming language for data science and backend development.', 'Python Browser Test', 'Computer Science')
    
    # Doc 2: Cooking
    upload_doc('cooking_test.txt', b'To make a great cake, you need flour, sugar, eggs, and butter. Bake at 350 degrees.', 'Cooking Browser Test', 'Cooking')
    
    print("Waiting 2 seconds for indexing...")
    time.sleep(2)
    print("Setup complete.")

if __name__ == "__main__":
    setup()
