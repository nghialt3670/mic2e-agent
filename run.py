from __future__ import annotations

import uvicorn

from app.config import UVICORN_LOG_CONFIG
from app.env import PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_config=UVICORN_LOG_CONFIG,
    )
