import requests
import json
from app import create_app

app = create_app()

def check_es_index():
    with app.app_context():
        es = app.elasticsearch
        index_name = "documents"
        
        print(f"Checking index: {index_name}")
        
        # Check if index exists
        if not es.indices.exists(index=index_name):
            print(f"Index '{index_name}' does NOT exist!")
            return
            
        # Get index stats
        stats = es.indices.stats(index=index_name)
        doc_count = stats['_all']['primaries']['docs']['count']
        print(f"Document count in index: {doc_count}")
        
        # Get mapping
        mapping = es.indices.get_mapping(index=index_name)
        print("Index Mapping:")
        print(json.dumps(mapping.body, indent=2))
        
        # Search all
        print("\nSearching all documents:")
        res = es.search(index=index_name, body={"query": {"match_all": {}}, "size": 5})
        print(f"Found {res['hits']['total']['value']} hits")
        for hit in res['hits']['hits']:
            print(f"ID: {hit['_id']}, Title: {hit['_source'].get('title')}")

if __name__ == "__main__":
    check_es_index()
