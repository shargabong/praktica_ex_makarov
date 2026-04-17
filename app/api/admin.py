from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_admin
from ..schemas import UserOut
from ..repositories import UserRepository

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return UserRepository(db).list_all()
