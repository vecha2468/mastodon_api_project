#created by Anil kumar
import unittest
from app import app
import json

class MastodonServiceTestCase(unittest.TestCase):
  
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    def test_create(self):
        response = self.app.post('/',
                                 data=json.dumps({'status': 'Hello World'}),
                                 content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('post_id', data)
        self.assertEqual(data['success'], True)

    def test_retrieve(self):
        post_data = {'status': 'Test Post'}
        post_response = self.app.post('/create', 
                                      data=json.dumps(post_data),
                                      content_type='application/json')
        post_id = json.loads(post_response.data)['post_id']
        
        response = self.app.get(f'/retrieve/{post_id}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['post']['status'], post_data['status'])
	#created by Sanjushree Golla
    def test_delete(self):
        post_data = {'status': 'Test Post for Deletion'}
        post_response = self.app.post('/create', 
                                      data=json.dumps(post_data),
                                      content_type='application/json')
        post_id = json.loads(post_response.data)['post_id']
        
        delete_response = self.app.delete(f'/delete/{post_id}')
        self.assertEqual(delete_response.status_code, 200)
        
        retrieve_response = self.app.get(f'/retrieve/{post_id}')
        data = json.loads(retrieve_response.data)
        self.assertEqual(retrieve_response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
