import praw
from urllib import parse, request
import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

IMGUR_CLIENT_ID = os.getenv('IMGUR_CLIENT_ID')
IMGUR_ALBUM_ID = os.getenv('IMGUR_ALBUM_ID')
IMGUR_ALBUM_URL = f"https://api.imgur.com/3/album/{IMGUR_ALBUM_ID}/images"
IMGUR_CLIENT_SECRET = os.getenv('IMGUR_CLIENT_SECRET')

with open("imgur.json", "r") as f:
    imgur_requests = json.load(f)

IMGUR_ACCESS_TOKEN = imgur_requests["access_token"]
IMGUR_REFRESH_TOKEN = imgur_requests["refresh_token"]
IMGUR_TOKEN_TYPE = imgur_requests["token_type"]

def generate_new_access_token() -> int:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        }
    payload = {
            "refresh_token": IMGUR_REFRESH_TOKEN,
            "client_id": IMGUR_CLIENT_ID,
            "client_secret": IMGUR_CLIENT_SECRET,
            "grant_type": "refresh_token"
        }
    print("[?] Attempting to get a new access token with the refresh token... ", end="")
    r2 = requests.post("https://api.imgur.com/oauth2/token", data=payload, headers=headers)
    print(r2.json())
    if r2.status_code == 200:
        print("Done")
        with open("imgur.json", "w") as f:
            json.dump(r2.json(), f)

        global IMGUR_ACCESS_TOKEN 
        IMGUR_ACCESS_TOKEN = r2.json()["access_token"] # Updates the access token
        return 0
    else:
        print("Failed")
        return -1

generate_new_access_token()
    
    