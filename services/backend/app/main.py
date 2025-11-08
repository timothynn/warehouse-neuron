from fastapi import FastAPI

from app.routes import stock

app = FastAPI(
    title="Warehouse Neuron API",
    description="Warehouse management system with stock tracking",
    version="0.1.0",
)

# Include routers
app.include_router(stock.router)


@app.get("/")
async def root():
    return {"message": "Warehouse Neuron API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
