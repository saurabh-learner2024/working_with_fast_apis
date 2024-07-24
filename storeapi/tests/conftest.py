# Import necessary libraries for testing
from typing import AsyncGenerator, Generator

import pytest  # Pytest is a testing framework for Python
from fastapi.testclient import TestClient  # TestClient allows interaction with the FastAPI app without starting the server
from httpx import AsyncClient, ASGITransport  # AsyncClient and ASGITransport are used to make async requests to our API
from storeapi.main import app  # Import the FastAPI app
from storeapi.routers.post import comment_table, post_table  # Import the tables used in the app

# Fixture to set the async backend to "asyncio" for the test session
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"  # This ensures async functions run with asyncio during the entire test session

# Fixture to create a synchronous TestClient instance for interacting with the API
@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)  # Provides a TestClient instance for making requests to the FastAPI app

# Fixture to clear the post and comment tables before each test
@pytest.fixture(autouse=True)  # This fixture will run automatically before every test
async def db() -> AsyncGenerator:
    post_table.clear()  # Clear the post_table to ensure a clean state for each test
    comment_table.clear()  # Clear the comment_table similarly
    yield  # Yield control back to the test

# Fixture to create an asynchronous client for making async requests
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    # Create an AsyncClient instance using ASGITransport and the base URL from the TestClient
    async with AsyncClient(transport=ASGITransport(app), base_url=client.base_url) as ac:
        yield ac  # Yield the AsyncClient instance for making requests
