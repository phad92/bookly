from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field

from src.db.models import Book
from src.books.schemas import BookCreateModel
from src.reviews.schemas import ReviewModel


class UserCreateModel(BaseModel):
    firstname: str 
    lastname: str
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)
    is_verified: bool = False

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    firstname: str
    lastname: str
    is_verified: bool 
    password_hash: str = Field(exclude=True)
    created_at: datetime 
    updated_at: datetime

class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewModel]


class UserLoginModel(BaseModel):
    email:str
    password: str

class EmailModel(BaseModel):
    addresses: List[str]

class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_password: str