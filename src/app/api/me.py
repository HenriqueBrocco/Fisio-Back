from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(tags=["me"])

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "role": user.role, "name": user.name, "email": user.email}
