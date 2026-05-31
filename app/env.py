import os

from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INFERENCE_API_URL = os.getenv("INFERENCE_API_URL")
STORAGE_API_URL = os.getenv("STORAGE_API_URL")

# Redis configuration - supports both "host:port" format and separate variables
REDIS_HOST_ENV = os.getenv("REDIS_HOST", "")
if ":" in REDIS_HOST_ENV:
    # Handle "host:port" format (backward compatibility)
    REDIS_HOST, REDIS_PORT_STR = REDIS_HOST_ENV.rsplit(":", 1)
    REDIS_PORT = int(REDIS_PORT_STR)
else:
    # Use separate REDIS_HOST and REDIS_PORT variables
    REDIS_HOST = REDIS_HOST_ENV if REDIS_HOST_ENV else "localhost"
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Validate Redis configuration
if not REDIS_HOST:
    raise ValueError("REDIS_HOST must be set. Use format 'host:port' or set REDIS_HOST and REDIS_PORT separately")
