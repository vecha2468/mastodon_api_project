# Created by Anil Kumar and Sanjushree Golla
import unittest
from unittest.mock import patch, MagicMock
from app import app
import json
from mastodon_service import InvalidInputError, RateLimitError, APIError

class MastodonServiceTestCase(unittest.TestCase):
    """
    Test suite for Mastodon service Flask application
    """
  
    def setUp(self):
        """
        Set up test environment before each test
        
        Creates a test client and enables testing mode for the Flask app
        """
        self.app = app.test_client()
        self.app.testing = True
        
    @patch('mastodon_service.requests.post')
    def test_create_success(self, mock_post):
        """
        Test successful post creation
        
        Verifies that the /create endpoint correctly 
        """
        #successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123456',
            'content': 'Hello World',
            'created_at': '2025-04-11T12:00:00Z'
        }
        mock_post.return_value = mock_response
        
        # Test the endpoint with valid data
        response = self.app.post('/create',
                              data=json.dumps({'status': 'Hello World'}),
                              content_type='application/json')
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('post_id', data)
        self.assertEqual(data['success'], True)
        
        mock_post.assert_called_once()
        
    @patch('mastodon_service.requests.post')
    def test_create_invalid_input(self, mock_post):
        """
        Test post creation with invalid input
        
        Verifies that the /create endpoint correctly handles 
        """
        # Test empty status
        response = self.app.post('/create',
                              data=json.dumps({'status': ''}),
                              content_type='application/json')
        
        # Assert proper error response for empty status
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertIn('error', data)
        
        # Test missing status field
        response = self.app.post('/create',
                              data=json.dumps({}),
                              content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        
        # Test non-JSON request
        response = self.app.post('/create',
                              data='Not JSON',
                              content_type='text/plain')
        
        # Assert proper error response for non-JSON
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        
    @patch('mastodon_service.requests.post')
    def test_create_rate_limit(self, mock_post):
        """
        Test handling of rate limiting during post creation
        """
        # Mock rate limited response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_response.text = 'Rate limit exceeded'
        mock_post.return_value = mock_response
        
        # Patch time.sleep to avoid waiting during tests
        with patch('time.sleep') as mock_sleep:
            response = self.app.post('/create',
                                  data=json.dumps({'status': 'Test post'}),
                                  content_type='application/json')
            
            # Assert rate limit was detected and handled properly
            self.assertEqual(response.status_code, 429)
            data = json.loads(response.data)
            self.assertEqual(data['success'], False)
            self.assertIn('rate limit', data['error'].lower())
            
            # Verify sleep was called (retries attempted)
            mock_sleep.assert_called()
            
    @patch('mastodon_service.requests.get')
    def test_retrieve_success(self, mock_get):
        """
        Test successful post retrieval
        
        Verifies that the /retrieve endpoint correctly fetches
        and returns post data when given a valid post ID.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123456',
            'content': 'Test Post',
            'created_at': '2025-04-11T12:00:00Z'
        }
        mock_get.return_value = mock_response
        
        # Test the retrieve endpoint
        response = self.app.get('/retrieve/123456')
        data = json.loads(response.data)
        
        # Assert results match expectations
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['post']['content'], 'Test Post')
        self.assertEqual(data['post']['id'], '123456')
        
        # Verify mock was called with correct URL
        mock_get.assert_called_once()
        call_args = mock_get.call_args[0][0]
        self.assertIn('123456', call_args)
        
    @patch('mastodon_service.requests.get')
    def test_retrieve_not_found(self, mock_get):
        """
        Test retrieval of non-existent post
        
        Verifies that the /retrieve endpoint correctly handles the case
        where the requested post ID does not exist.
        """
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_get.return_value = mock_response
        
        # Test the endpoint with non-existent ID
        response = self.app.get('/retrieve/nonexistent')
        data = json.loads(response.data)
        
        # Assert proper error response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertIn('error', data)
        
    @patch('mastodon_service.requests.delete')
    def test_delete_success(self, mock_delete):
        """
        Test successful post deletion
        
        Verifies that the /delete endpoint correctly handles requests
        to delete a post when given a valid post ID.
        
        successful delete response from the API.
        """
        #  API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        # Test the delete endpoint
        response = self.app.delete('/delete/123456')
        data = json.loads(response.data)
        
        # Assert success response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
        # Verify mock was called with correct URL
        mock_delete.assert_called_once()
        call_args = mock_delete.call_args[0][0]
        self.assertIn('123456', call_args)
        
    @patch('mastodon_service.requests.delete')
    def test_delete_not_found(self, mock_delete):
        """
        Test deletion of non-existent post
        
        Verifies that the /delete endpoint correctly handles the case
        where the post ID to delete does not exist.
        
       404 Not Found response from the API.
        """
        # 404 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_delete.return_value = mock_response
        
        # Test deleting non-existent post
        response = self.app.delete('/delete/nonexistent')
        data = json.loads(response.data)
        
        # Assert proper error response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        
    @patch('mastodon_service.requests.post')
    def test_api_error_handling(self, mock_post):
        """
        Test handling of general API errors
        
        Verifies that the application correctly handles unexpected
        server errors from the Mastodon API.
        
         500 Internal Server Error response.
        """
        #  error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal server error'
        mock_post.return_value = mock_response
        
        # Test endpoint with server error
        response = self.app.post('/create',
                              data=json.dumps({'status': 'Test post'}),
                              content_type='application/json')
        
        # Assert error was handled properly
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertIn('error', data)
        
    @patch('mastodon_service.requests.post')
    def test_network_error_handling(self, mock_post):
        """
        Test handling of network errors
        
        Verifies that the application correctly handles network-level
        exceptions that might occur during API requests.
        
        Mocks a connection exception during the request.
        """
        #  request exception
        mock_post.side_effect = Exception("Connection error")
        
        # Patch time.sleep to avoid waiting during tests
        with patch('time.sleep'):
            response = self.app.post('/create',
                                  data=json.dumps({'status': 'Test post'}),
                                  content_type='application/json')
            
            # Assert error was handled properly
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertEqual(data['success'], False)
            self.assertIn('error', data)
            
    def test_home_page_loads(self):
        """
        Test that the home page loads correctly
        
        Verifies that the main index route returns a valid HTML page.
        """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_long_post_validation(self):
        """
        Test validation of too-long posts
        
        Verifies that the application correctly rejects posts that
        exceed the Mastodon character limit (500 chars).
        """
        # Create a post with >500 characters
        long_status = "x" * 501
        response = self.app.post('/create',
                              data=json.dumps({'status': long_status}),
                              content_type='application/json')
        
        # Assert validation error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertIn('character limit', data['error'].lower())

# Run the tests when the script is executed directly
if __name__ == "__main__":
    unittest.main()