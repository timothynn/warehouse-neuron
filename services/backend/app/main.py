from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import stock, skus, inventory, auth, users

app = FastAPI(
    title="Warehouse Neuron API",
    description="Warehouse management system with stock tracking and authentication",
    version="0.2.0",
)

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

# Include routers
app.include_router(auth.router)  # Authentication routes
app.include_router(users.router)  # User management routes
app.include_router(stock.router)
app.include_router(skus.router)
app.include_router(inventory.router)


@app.get("/")
async def root():
    return {"message": "Warehouse Neuron API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
