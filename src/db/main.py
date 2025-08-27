from sqlmodel import create_engine, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config


# Create an asynchronous engine for the database connection
engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=False,
    )
)

async def init_db():
    """Initialize the database connection."""
    async with engine.begin() as conn:

        await conn.run_sync(SQLModel.metadata.create_all)
        # Here you can create tables or perform other setup tasks
        print("Database connection initialized.")

    
    # Optionally, you can also create a session factory
    return AsyncSession(engine)


from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a new session for database operations."""
    Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session