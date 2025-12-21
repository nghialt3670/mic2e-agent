from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.lifespan import lifespan
from app.routes.chat2edit_routes import router as chat2edit_router
from app.routes.health_routes import router as health_router

app = FastAPI(lifespan=lifespan)

# Allow frontend (different origin/port) to call polling endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(chat2edit_router)
app.include_router(health_router)
