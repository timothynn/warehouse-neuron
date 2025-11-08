# Test configuration and fixtures
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.models import Base
from app.database import get_session
from app.main import app

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://wn_user:wn_pass@localhost:5434/warehouse_neuron_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """Create a test database session."""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(session):
    """Create a test client with overridden dependencies."""
    from fastapi.testclient import TestClient
    
    async def override_get_session():
        yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
