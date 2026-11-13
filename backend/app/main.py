from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
import app.models  # Ensures all models are registered on Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables on startup (perfect for Render deployment)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="QR-Based Temporary Communication Platform API",
    description="Privacy-preserving lost-and-found communication system connecting owners and anonymous finders.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix="/api/v1")

# Mount Real-Time WebSocket routes
from app.websocket.handler import router as ws_router
app.include_router(ws_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "QR-Based Temporary Communication API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
