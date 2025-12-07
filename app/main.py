from fastapi import FastAPI

from app.lifespan import lifespan
from app.routes.chat2edit_routes import router as chat2edit_router
from app.routes.health_routes import router as health_router

app = FastAPI(lifespan=lifespan)

app.include_router(chat2edit_router)
app.include_router(health_router)
