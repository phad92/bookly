
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import Book
from src.books.service import BookService
from src.books.schemas import BookCreateModel, BookDetailModel, BookUpdateModel  # Assuming you have a book_data
from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer, RoleChecker


router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(['admin', 'user']))

@router.get("/", response_model=List[Book], dependencies=[role_checker])

async def get_books(session: AsyncSession = Depends(get_session), token_details:dict = Depends(access_token_bearer)) -> List[BookDetailModel]:
    """Fetch all books."""
    print("token_details:dict", token_details)
    books = await book_service.get_books(session)
    return books

@router.get("/user/{user_uid}", response_model=List[Book], dependencies=[role_checker])
async def get_user_book_submissions(user_uid: str, session: AsyncSession = Depends(get_session), token_details:dict = Depends(access_token_bearer)) -> List[BookDetailModel]:
    """Fetch all user books."""
    books = await book_service.get_user_books(user_uid, session)
    return books

@router.post("/", status_code= status.HTTP_201_CREATED, response_model=BookCreateModel, dependencies=[role_checker])
async def create_book(book: BookCreateModel, session: AsyncSession = Depends(get_session), token_details:dict = Depends(access_token_bearer)) -> dict:
    """Create a new book."""
    user_uid = token_details.get('user')['user_uid']
    book_data = book.model_dump()
    new_book = await book_service.create_book(book, user_uid, session)
    if not new_book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book creation failed")
    
    return book_data


@router.get("/{book_id}", dependencies=[role_checker], response_model=BookDetailModel)
async def get_book(book_id: str, session: AsyncSession = Depends(get_session), token_details:dict = Depends(access_token_bearer)) -> dict:
    """Fetch a book by its ID."""
    book = await book_service.get_book(book_id, session)

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    print(f"Retrieved book: {book}")
    return book  # Convert to dict if needed
    


@router.put("/{book_id}", response_model=Book, dependencies=[role_checker])
async def update_book(book_id: str, updated_book: BookUpdateModel, session: AsyncSession = Depends(get_session), token_details:dict = Depends(access_token_bearer)):
    """Update a book by its ID."""
    updated = await book_service.update_book(book_id, updated_book, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    return updated

@router.delete("/{book_id}", dependencies=[role_checker])
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session), token_details:dict = Depends(access_token_bearer)) -> dict:
    """Delete a book by its ID."""
    deleted = await book_service.delete_book(book_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    return {"message": "Book deleted successfully"}