from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="System and Database Health Check",
    tags=["Health"],
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Verifies that the application server is responsive and the database connection is live."""
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"disconnected: {str(exc)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "service": "qr-temporary-communication-api",
        "version": "1.0.0",
    }
