from app import create_app
from app.models.document import Document

app = create_app()

with app.app_context():
    count = app.db.documents.count_documents({})
    print(f"Total documents: {count}")
    docs = app.db.documents.find().limit(5)
    for doc in docs:
        print(f"Title: {doc.get('title')}")
