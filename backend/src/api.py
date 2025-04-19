import os

from dotenv import load_dotenv

def get_openai_key() -> str:
    load_dotenv()
    return os.environ.get("OPENAI_API_KEY")