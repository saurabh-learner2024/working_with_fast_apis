from httpx import AsyncClient  # Import AsyncClient for making async HTTP requests
import pytest  # Import pytest for writing and running tests


# Function to create a new post by sending an HTTP POST request to the "/post" endpoint
async def create_post(body: str, async_client: AsyncClient) -> dict:
    # Send a POST request to the "/post" endpoint with the given post content
    response = await async_client.post("/post", json={"body": body})
    # Return the JSON response from the server, which includes the post details
    return response.json()


# Function to create a new comment by sending an HTTP POST request to the "/comment" endpoint
async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    # Send a POST request to the "/comment" endpoint with the given comment content and post ID
    response = await async_client.post(
        "/comment", json={"body": body, "post_id": post_id}
    )
    # Return the JSON response from the server, which includes the comment details
    return response.json()


# Fixture to create a post before each test
@pytest.fixture()
async def created_post(async_client: AsyncClient):
    # Use the create_post function to create a post with the body "Test Post"
    return await create_post("Test Post", async_client)


# Fixture to create a comment before each test
@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict):
    # Use the create_comment function to create a comment for the previously created post
    return await create_comment("Test Comment", created_post["id"], async_client)


# Test to check if a post can be created successfully
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_create_post(async_client: AsyncClient):
    body = "Test Post"
    # Send a POST request to create a new post with the specified body content
    response = await async_client.post(
        "/post",
        json={"body": body}
    )
    # Assert that the response status code is 201 (Created), indicating success
    assert response.status_code == 201
    # Assert that the response contains the correct post data
    assert {"id": 1, "body": body}.items() <= response.json().items()


# Test to check the behavior when creating a post with missing data
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_create_post_missing_data(async_client: AsyncClient):
    # Send a POST request to create a new post with no data
    response = await async_client.post("/post", json={})
    # Assert that the response status code is 422 (Unprocessable Entity), indicating a validation error
    assert response.status_code == 422


# Test to check if all posts can be retrieved
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    # Send a GET request to retrieve all posts
    response = await async_client.get("/post")
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON matches the created post
    assert response.json() == [created_post]


# Test to check if a comment can be created successfully
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_create_comment(async_client: AsyncClient, created_post: dict):
    body = "Test Comment"
    # Send a POST request to create a new comment on the specified post
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": created_post["id"]}
    )
    # Assert that the response status code is 201 (Created), indicating success
    assert response.status_code == 201
    # Assert that the response contains the correct comment data
    assert {
               "id": 1,
               "body": body,
               "post_id": created_post["id"],
           }.items() <= response.json().items()


# Test to check if comments on a post can be retrieved
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_get_comments_on_post(
        async_client: AsyncClient, created_post: dict, created_comment: dict
):
    # Send a GET request to retrieve comments for the specified post
    response = await async_client.get(f"/post/{created_post['id']}/comment")
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON contains the created comment
    assert response.json() == [created_comment]


# Test to check if a post with no comments returns an empty list of comments
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_get_comments_on_post_empty(
        async_client: AsyncClient, created_post: dict
):
    # Send a GET request to retrieve comments for the specified post
    response = await async_client.get(f"/post/{created_post['id']}/comment")
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON is an empty list, indicating no comments
    assert response.json() == []


# Test to check if a post with its comments can be retrieved
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_get_post_with_comments(
        async_client: AsyncClient, created_post: dict, created_comment: dict
):
    # Send a GET request to retrieve a post and its comments
    response = await async_client.get(f"/post/{created_post['id']}")
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON includes the post and its comments
    assert response.json() == {
        "post": created_post,
        "comments": [created_comment]
    }


# Test to check if a request for a non-existent post returns a 404 error
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_get_missing_post_with_comments(
        async_client: AsyncClient, created_post: dict, created_comment: dict
):
    # Send a GET request to retrieve a post with an ID that does not exist
    response = await async_client.get(f"/post/2")
    # Assert that the response status code is 404 (Not Found), indicating that the post was not found
    assert response.status_code == 404
