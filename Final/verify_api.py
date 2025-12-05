import unittest
import json
import io
from app import create_app
from app.services.embedding_service import EmbeddingService

class TestTeacherAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['MONGODB_DB_NAME'] = 'smart_library_test'
        self.client = self.app.test_client()
        
        # Clear test db
        self.app.mongo.drop_database('smart_library_test')

    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'healthy')
        print("[OK] Health check passed")

    def test_document_flow(self):
        # 1. Upload
        data = {
            'file': (io.BytesIO(b'This is a test document content for verification.'), 'test_doc.txt'),
            'title': 'Test Document',
            'subject': 'Computer Science',
            'document_type': 'note'
        }
        response = self.client.post('/api/documents', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 201)
        doc_id = response.json['document']['id']
        print("[OK] Upload passed")

        # 2. Get Documents
        response = self.client.get('/api/documents')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json['documents']), 1)
        print("[OK] List documents passed")

        # 3. Search
        search_data = {
            'query': 'test',
            'search_type': 'keyword'
        }
        response = self.client.post('/api/search', json=search_data)
        self.assertEqual(response.status_code, 200)
        print("[OK] Search passed")

        # 4. Like
        response = self.client.post(f'/api/documents/{doc_id}/like')
        self.assertEqual(response.status_code, 200)
        print("[OK] Like passed")

        # 5. Review
        review_data = {
            'text': 'Great doc!',
            'rating': 5,
            'author': 'Teacher'
        }
        response = self.client.post(f'/api/documents/{doc_id}/review', json=review_data)
        self.assertEqual(response.status_code, 200)
        print("[OK] Review passed")

        # 6. Delete
        response = self.client.delete(f'/api/documents/{doc_id}')
        self.assertEqual(response.status_code, 200)
        print("[OK] Delete passed")

    def test_admin_stats(self):
        response = self.client.get('/api/admin/stats')
        self.assertEqual(response.status_code, 200)
        self.assertIn('documents', response.json)
        print("[OK] Admin stats passed")

if __name__ == '__main__':
    unittest.main()
