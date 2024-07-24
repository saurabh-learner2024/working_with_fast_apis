from httpx import AsyncClient  # Import AsyncClient for making async HTTP requests
import pytest  # Import pytest for writing and running tests


# Function to create a new post by sending an HTTP POST request to the "/post" endpoint
async def create_post(body: str, async_client: AsyncClient) -> dict:
    # Send a POST request to the "/post" endpoint with the provided body
    response = await async_client.post("/post", json={"body": body})
    # Return the JSON response from the server
    return response.json()


async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/comment", json={"body": body, "post_id": post_id}
    )
    return response.json()


# Fixture to create a post before each test
@pytest.fixture()
async def created_post(async_client: AsyncClient):
    # Use the create_post function to create a post with a predefined body
    return await create_post("Test Post", async_client)


@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict):
    return await create_comment("Test Comment", created_post["id"], async_client)


# Test to verify that a post can be created successfully
@pytest.mark.anyio  # Indicates that this is an async test that should run with the anyio plugin
async def test_create_post(async_client: AsyncClient):
    body = "Test Post"
    # Send a POST request to create a new post
    response = await async_client.post(
        "/post",
        json={"body": body}
    )
    # Check if the status code is 201 (Created)
    assert response.status_code == 201
    # Check if the response JSON contains the expected post data
    assert {"id": 0, "body": body}.items() <= response.json().items()


# Test to verify the behavior when creating a post with missing data
@pytest.mark.anyio  # Indicates that this is an async test that should run with the anyio plugin
async def test_create_post_missing_data(async_client: AsyncClient):
    # Send a POST request to create a new post with no data
    response = await async_client.post("/post", json={})
    # Check if the status code is 422 (Unprocessable Entity), which indicates a validation error
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post")
    assert response.status_code == 200
    assert response.json() == [created_post]


@pytest.mark.anyio
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    body = "Test Comment"

    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": created_post["id"]}
    )
    assert response.status_code == 201
    assert {
               "id": 0,
               "body": body,
               "post_id": created_post["id"],
           }.items() <= response.json().items()


@pytest.mark.anyio
async def test_get_comments_on_post(
        async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comment")
    assert response.status_code == 200
    assert response.json() == [created_comment]


@pytest.mark.anyio
async def test_get_comments_on_post_empty(
        async_client: AsyncClient, created_post: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comment")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_get_post_with_comments(
        async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "post": created_post,
        "comments": [created_comment]
    }


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
        async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/2")

    assert response.status_code == 404

