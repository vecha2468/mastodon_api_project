import os
import requests
from dotenv import load_dotenv

load_dotenv()
#created by Sanjushree Golla
BASE_URL = "https://mastodon.social/api/v1"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def create(text):
    response = requests.post(
        f"{BASE_URL}/statuses",
        headers=headers,
        data={"status": text}
    )
    return response.json()
#created by Sreya Atluri
def retrieve(post_id):
    response = requests.get(f"{BASE_URL}/statuses/{post_id}", headers=headers)
    return response.json()
#created by Sanjushree Golla
def delete(post_id):
    response = requests.delete(f"{BASE_URL}/statuses/{post_id}", headers=headers)
    return response.status_code == 200
