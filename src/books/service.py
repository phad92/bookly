from datetime import datetime
from typing import List
from unittest import result
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Book
from .schemas import BookModel, BookCreateModel, BookUpdateModel

class BookService:
    async def get_books(self, session: AsyncSession):
        """Fetch all books from the database."""
        statement = select(Book).order_by(desc(Book.created_at))
        
        result = await session.exec(statement)

        return result.all()
    
    async def get_user_books(self, user_uid, session: AsyncSession):
        """Fetch all books from the database."""
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))
        
        result = await session.exec(statement)

        return result.all()
    


    async def get_book(self, book_id: int, session: AsyncSession):
        """Fetch a single book by its ID."""
        statement = select(Book).where(Book.uid == book_id)
        result = await session.exec(statement)

        book = result.first()

        return book if book else None

    async def create_book(self, book: BookCreateModel, user_uid: str, session: AsyncSession):
        """Create a new book in the database."""
        book_dic = book.model_dump()

        new_book = Book(**book_dic)
        new_book.user_uid = user_uid
        new_book.published_date = datetime.strptime(book_dic['published_date'], "%Y-%m-%d")

        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(self, book_id: int, book: BookUpdateModel, session: AsyncSession):
        """Update an existing book by its ID."""
        
        book_to_update = await self.get_book(book_id, session)
        if not book_to_update:
            return None
        
        book_data = book.model_dump(exclude_unset=True)
        for key, value in book_data.items():
            setattr(book_to_update, key, value)

        await session.commit()

        return book_to_update

    async def delete_book(self, book_id: int, session: AsyncSession):
        """Delete a book by its ID."""
        book_to_delete = await self.get_book(book_id, session)
        if not book_to_delete:
            return None
        
        await session.delete(book_to_delete)
        await session.commit()
        return book_to_delete