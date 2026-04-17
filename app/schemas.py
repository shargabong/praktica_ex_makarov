import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator

class RegisterRequest(BaseModel):
    email: str
    username: str
    phone: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, value):
            raise ValueError("Некорректный email")
        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        pattern = r"^[a-zA-Z][a-zA-Z0-9_]{2,19}$"
        if not re.match(pattern, value):
            raise ValueError("Username должен начинаться с буквы и содержать 3-20 символов")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        pattern = r"^\+7-\d{3}-\d{3}-\d{2}-\d{2}$"
        if not re.match(pattern, value):
            raise ValueError("Телефон должен быть в формате +7-900-123-45-67")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not re.search(r"[A-Z]", value) or not re.search(r"[a-z]", value) or not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать заглавную букву, строчную и цифру")
        return value

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    phone: str
    role: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if len(value.strip()) < 3:
            raise ValueError("Название задачи должно содержать минимум 3 символа")
        return value.strip()

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value and value not in {"new", "in_progress", "done"}:
            raise ValueError("Недопустимый статус")
        return value

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    owner_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)