# Created by Sanjushree Golla, Sreya Atluri
# Created with error handling and rate limiting support
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------
# Service Configuration
# ------------------------------
# Base URL for the Mastodon API
BASE_URL = "https://mastodon.social/api/v1"
# Get API token from environment variables for security
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
# Number of retry attempts when rate limited
MAX_RETRIES = 3
# Default delay in seconds between retries
RETRY_DELAY = 60  # seconds to wait when rate limited

# Default headers for all API requests
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}


# Custom Exception Classes

class MastodonServiceError(Exception):
    """Base exception for Mastodon service errors
    All service-specific exceptions inherit from this base class"""
    pass

class RateLimitError(MastodonServiceError):
    """Exception raised when API rate limit is hit
    Indicates the client should wait before making new requests"""
    pass

class InvalidInputError(MastodonServiceError):
    """Exception raised for invalid inputs
    This includes empty fields, malformed data, or fields exceeding limits"""
    pass

class APIError(MastodonServiceError):
    """Exception raised for general API errors
    This includes server errors, authentication failures, and network issues"""
    pass


# Service Functions


# Created by Sanjushree Golla
def create(text):
    """
    Create a new post (status) on Mastodon
    """
    # Input validation - check if text exists and is a string or not
    if not text or not isinstance(text, str):
        raise InvalidInputError("Status text cannot be empty and must be a string")
    
    # Check character count 
    if len(text) > 500:  # Mastodon character limit
        raise InvalidInputError("Status text exceeds the 500 character limit")
    
    # Attempt to post with retry logic for rate limits
    for attempt in range(MAX_RETRIES):
        try:
            # Send the post request to the API
            response = requests.post(
                f"{BASE_URL}/statuses",
                headers=headers,
                data={"status": text},
                timeout=10  
            )
            
            # Process response based on status code
            if response.status_code == 200 or response.status_code == 201:
               
                return response.json()
            elif response.status_code == 429:  # Rate limited
                if attempt < MAX_RETRIES - 1:
                    retry_after = int(response.headers.get('Retry-After', RETRY_DELAY))
                    time.sleep(retry_after)
                    continue
                else:
                    # Max retries reached, inform caller about rate limit
                    raise RateLimitError(f"Rate limit exceeded after {MAX_RETRIES} attempts")
            elif response.status_code == 400:
                error_data = response.json()
                raise InvalidInputError(f"Invalid input: {error_data.get('error', 'Unknown error')}")
            elif response.status_code == 401:
                # Authentication failure
                raise APIError("Authentication failed. Check your access token.")
            else:
                # Other API errors
                raise APIError(f"API error: {response.status_code}, {response.text}")
                
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise APIError(f"Request failed: {str(e)}")
    
    # This code should never be reached if retry logic is working
    raise APIError("Maximum retries exceeded")

# Created by Sreya Atluri
def retrieve(post_id):
    """
    Retrieve a post from Mastodon by its ID
    """
    # Input validation to prevent unnecessary API calls
    if not post_id:
        raise InvalidInputError("Post ID cannot be empty")
    
    # Attempt to retrieve with retry logic
    for attempt in range(MAX_RETRIES):
        try:
            # Send the GET request to fetch post data
            response = requests.get(
                f"{BASE_URL}/statuses/{post_id}", 
                headers=headers,
                timeout=10  
            )
            
            # Process response based on status code
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise InvalidInputError(f"Post with ID {post_id} not found")
            elif response.status_code == 429:  # Rate limited
                if attempt < MAX_RETRIES - 1:
                    retry_after = int(response.headers.get('Retry-After', RETRY_DELAY))
                    # Wait before next attempt
                    time.sleep(retry_after)
                    continue
                else:
                    raise RateLimitError(f"Rate limit exceeded after {MAX_RETRIES} attempts")
            else:
                # Other API errors
                raise APIError(f"API error: {response.status_code}, {response.text}")
                
        except requests.RequestException as e:
            # Handle network-level errors
            if attempt < MAX_RETRIES - 1:
                # Retry after delay
                time.sleep(RETRY_DELAY)
                continue
            raise APIError(f"Request failed: {str(e)}")
    
    # This code should never be reached if retry logic is working
    raise APIError("Maximum retries exceeded")

# Created by Sanjushree Golla
def delete(post_id):
    """
    Delete a post from Mastodon by its ID
    """
    # Input validation to prevent unnecessary API calls
    if not post_id:
        raise InvalidInputError("Post ID cannot be empty")
    
    # Attempt to delete with retry logic
    for attempt in range(MAX_RETRIES):
        try:
            # Send the DELETE request
            response = requests.delete(
                f"{BASE_URL}/statuses/{post_id}", 
                headers=headers,
                timeout=10 
            )
            
            # Process response based on status code
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                raise InvalidInputError(f"Post with ID {post_id} not found")
            elif response.status_code == 429:  # Rate limited
                if attempt < MAX_RETRIES - 1:
                    retry_after = int(response.headers.get('Retry-After', RETRY_DELAY))
                    # Wait before next attempt
                    time.sleep(retry_after)
                    continue
                else:
                    raise RateLimitError(f"Rate limit exceeded after {MAX_RETRIES} attempts")
            else:
                # Other API errors
                raise APIError(f"API error: {response.status_code}, {response.text}")
                
        except requests.RequestException as e:
            # Handle network-level errors
            if attempt < MAX_RETRIES - 1:
                # Retry after delay
                time.sleep(RETRY_DELAY)
                continue
            raise APIError(f"Request failed: {str(e)}")
    
    # This code should never be reached if retry logic is working
    raise APIError("Maximum retries exceeded")