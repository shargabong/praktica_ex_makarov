from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..schemas import TaskCreate, TaskUpdate, TaskOut
from ..services import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskOut, status_code=201)
def create(data: TaskCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return TaskService(db).create_task(user.id, data)

@router.get("/", response_model=List[TaskOut])
def list_tasks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return TaskService(db).list_tasks(user.id)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return TaskService(db).get_task_for_user(task_id, user)

@router.patch("/{task_id}", response_model=TaskOut)
def update(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return TaskService(db).update_task(task_id, data, user)

@router.delete("/{task_id}")
def delete(task_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    TaskService(db).delete_task(task_id, user)
    return {"message": "Удалено"}
