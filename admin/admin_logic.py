import os
import json

# Hårdkodat lösenord
ADMIN_PASSWORD = "hemligt123"

# Sökväg till newspapers.json
BASE_DIR = os.path.dirname(__file__)
JSON_PATH = os.path.join(BASE_DIR, 'newspapers.json')

def get_admin_password():
    return ADMIN_PASSWORD

def load_newspapers():
    if not os.path.exists(JSON_PATH):
        return []
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_newspapers(papers):
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
