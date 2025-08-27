from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.books.routes import router as books_router
from src.auth.routes import auth_router
from src.middleware import register_middleware
from src.reviews.routes import review_router

from contextlib import asynccontextmanager
from src.db.main import init_db
from src.errors import (
    create_exception_handler,
    InvalidToken,
    RevokedToken,
    AccessTokenRequired,
    register_all_errors,
)


# setting up a lifespan event for the FastAPI application
# This allows for setup and teardown actions when the application starts and stops
# Installed alembic for migration cmd: alembic init -t async migrations
# alembic revision --autogenerate -m "init"  (after configuration)
# alembic upgrade head to run migration
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This is where you can initialize resources or connections
    print("Starting up...")
    await init_db()
    yield
    # This is where you can clean up resources or connections
    print("Shutting down...")


# pip freeze > requirements.txt => to generate requirements.txt
# uvicorn src.__init__:app --reload => to run the app

version = "v1"
app = FastAPI(
    title="Bookly API",
    description="A simple REST API for managing book reviews",
    version=version,
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    contact={"email": "fadlu.haruna@gmail.com"},
    # lifespan=lifespan,
)

register_all_errors(app)
register_middleware(app)
# #repeat for all other error handlers
# app.add_exception_handler(
#     InvalidToken,
#     create_exception_handler(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         initial_detail={
#             "message": "Token is invalid or expired",
#             "error_code": "invalid_token",
#         },
#     ),
# )

# @app.exception_handler(500)
# async def internal_server_error(request, exec):
#     return JSONResponse(
#         content={
#             "message": "Oops! Something went wrong",
#             "error_code": "server_error"
#         },
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#     )

app.include_router(books_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
