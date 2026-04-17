import json
from fastapi import HTTPException
from .repositories import UserRepository, TaskRepository
from .database import redis_client
from .security import verify_password

class AuthService:
    def __init__(self, db):
        self.repo = UserRepository(db)

    def register_user(self, data):
        if self.repo.get_by_login(data.email) or self.repo.get_by_login(data.username):
            raise HTTPException(status_code=400, detail="Пользователь с таким email или username уже существует")
        return self.repo.create(data.email, data.username, data.phone, data.password)

    def authenticate_user(self, login, password):
        user = self.repo.get_by_login(login)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

class TaskService:
    def __init__(self, db):
        self.repo = TaskRepository(db)

    def _cache_key(self, user_id): 
        return f"user:{user_id}:tasks"

    def create_task(self, user_id, data):
        task = self.repo.create(user_id, data.title, data.description or "")
        if redis_client:
            redis_client.delete(self._cache_key(user_id))
        return task

    def list_tasks(self, user_id):
        key = self._cache_key(user_id)
        if redis_client:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        
        tasks = self.repo.list_by_owner(user_id)
        res = [{"id": t.id, "title": t.title, "description": t.description, "status": t.status, 
                "owner_id": t.owner_id, "created_at": t.created_at.isoformat()} for t in tasks]
        
        if redis_client:
            redis_client.setex(key, 60, json.dumps(res))
        return res

    def get_task_for_user(self, task_id, current_user):
        task = self.repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        if task.owner_id != current_user.id and current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Нет доступа к этой задаче")
        return task

    def update_task(self, task_id, data, current_user):
        task = self.get_task_for_user(task_id, current_user)
        if data.title is not None: task.title = data.title
        if data.description is not None: task.description = data.description
        if data.status is not None: task.status = data.status
        
        updated = self.repo.update(task)
        if redis_client:
            redis_client.delete(self._cache_key(task.owner_id))
        return updated

    def delete_task(self, task_id, current_user):
        task = self.get_task_for_user(task_id, current_user)
        owner_id = task.owner_id
        self.repo.delete(task)
        if redis_client:
            redis_client.delete(self._cache_key(owner_id))