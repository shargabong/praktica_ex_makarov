from sqlalchemy.orm import Session
from sqlalchemy import or_
from .models import User, Task
from .security import hash_password

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_login(self, login: str):
        """Поиск пользователя по email или username"""
        return self.db.query(User).filter(
            or_(User.email == login, User.username == login)
        ).first()

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email, username, phone, password, role="user"):
        user = User(
            email=email, 
            username=username, 
            phone=phone, 
            hashed_password=hash_password(password), 
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_all(self):
        return self.db.query(User).all()

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, owner_id, title, description):
        task = Task(owner_id=owner_id, title=title, description=description)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_by_owner(self, owner_id):
        return self.db.query(Task).filter(Task.owner_id == owner_id).all()

    def get_by_id(self, task_id):
        return self.db.query(Task).filter(Task.id == task_id).first()

    def update(self, task):
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task):
        self.db.delete(task)
        self.db.commit()