from fastapi import APIRouter

from app.api.v1.endpoints import auth, contact, health, notifications, profile, qr, rooms

api_router = APIRouter()

# Register endpoint routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(qr.router, prefix="/qr", tags=["QR Identity"])
api_router.include_router(profile.router, prefix="/profile", tags=["Owner Profile"])
api_router.include_router(contact.router, prefix="/contact", tags=["Finder Contact & Rooms"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["Room Lifecycle"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
