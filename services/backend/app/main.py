from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.routes import stock, skus, inventory  # , auth, users
from app.middleware.error_handler import (
    sqlalchemy_exception_handler,
    value_error_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.middleware.logging_middleware import log_requests_middleware

app = FastAPI(
    title="Warehouse Neuron API",
    description="Warehouse management system with stock tracking and authentication",
    version="0.2.0",
)

# Register exception handlers FIRST, before middleware
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Configure CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Flutter web dev server
        "http://127.0.0.1:3000",
        "http://localhost:8080",  # Alternative ports
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request/response logging middleware
app.middleware("http")(log_requests_middleware)

# Include routers
# TODO: Re-enable auth after async conversion is complete
# app.include_router(auth.router)  # Authentication routes
# app.include_router(users.router)  # User management routes
app.include_router(stock.router)
app.include_router(skus.router)
app.include_router(inventory.router)


@app.get("/")
async def root():
    return {"message": "Warehouse Neuron API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
