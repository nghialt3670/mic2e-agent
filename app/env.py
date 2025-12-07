import os

from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INFERENCE_HOST = os.getenv("INFERENCE_HOST")
STORAGE_HOST = os.getenv("STORAGE_HOST")
