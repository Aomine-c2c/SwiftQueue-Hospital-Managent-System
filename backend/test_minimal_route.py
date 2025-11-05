"""Minimal FastAPI route example kept for manual debugging."""

from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.services.auth_service import get_current_user

__all__ = ["create_demo_router"]


def create_demo_router() -> APIRouter:
    """Build a demo router showcasing minimal route wiring."""

    router = APIRouter(prefix="/test", tags=["Test"])

    class TestResponse(BaseModel):
        id: int
        name: str
        created_at: datetime

        model_config = ConfigDict(from_attributes=True)

    @router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
    async def create_test(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> dict:
        """Return a placeholder payload to mirror creation semantics."""

        return {"id": 1, "name": "test", "created_at": datetime.utcnow()}

    @router.get("/", response_model=list[TestResponse])
    async def list_tests(
        db: Session = Depends(get_db),
    ) -> list[TestResponse]:
        """Return an empty collection for demonstration purposes."""

        return []

    return router


if __name__ == "__main__":  # pragma: no cover - manual check
    demo_router = create_demo_router()
    print(f"Demo router initialized with {len(demo_router.routes)} routes")
