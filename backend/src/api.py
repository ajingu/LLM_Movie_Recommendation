import os

from dotenv import load_dotenv

def get_api_key(key_name: str) -> str:
    load_dotenv()
    return os.environ.get(key_name)