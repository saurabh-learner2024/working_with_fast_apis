# Import necessary libraries for testing
import os
from typing import AsyncGenerator, Generator

import pytest  # Pytest is a testing framework for Python
from fastapi.testclient import \
    TestClient  # TestClient allows interaction with the FastAPI app without starting the server
from httpx import AsyncClient, ASGITransport  # AsyncClient and ASGITransport are used to make async requests to our API

os.environ["ENV_STATE"] = "test"
from storeapi.database import database, user_table
from storeapi.main import app  # Import the FastAPI app


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
    await database.connect()
    yield  # Yield control back to the test
    await database.disconnect()


# Fixture to create an asynchronous client for making async requests
@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    # Create an AsyncClient instance using ASGITransport and the base URL from the TestClient
    async with AsyncClient(transport=ASGITransport(app), base_url=client.base_url) as ac:
        yield ac  # Yield the AsyncClient instance for making requests


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.net", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details
