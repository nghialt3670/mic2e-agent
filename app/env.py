import os

from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INFERENCE_API_URL = os.getenv("INFERENCE_API_URL")
STORAGE_API_URL = os.getenv("STORAGE_API_URL")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
