# from datetime import datetime
# from typing import List, Optional
# import uuid
# from sqlmodel import Column, Field, Relationship, SQLModel
# import sqlalchemy.dialects.postgresql as pg
# from src.books import models

# class User(SQLModel, table=True):
#     __tablename__ = 'users'
#     uid: uuid.UUID = Field(
#         sa_column= Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
#     )
#     username: str
#     email: str
#     firstname: str
#     lastname: str
#     role: str = Field(
#         sa_column=Column(
#             pg.VARCHAR, nullable=False, server_default="user"
#         )
#     )
#     is_verified: bool = Field(default=False)
#     password_hash: str = Field(exclude=True)
#     created_at: datetime =  Field(
#         sa_column=Column(pg.TIMESTAMP, nullable=False, default=datetime.now),
#     )
#     updated_at: datetime =  Field(
#         sa_column=Column(pg.TIMESTAMP, nullable=False, default=datetime.now),
#     )
#     books: List["models.Book"] = Relationship(back_populates="user", sa_relationship_kwargs={'lazy': 'selectin'})

#     def __repr__(self):
#         return f"<User username={self.username}>"
