from httpx import AsyncClient  # Import AsyncClient for making async HTTP requests
import pytest  # Import pytest for writing and running tests

from storeapi import security


# Function to create a new post by sending an HTTP POST request to the "/post" endpoint
async def create_post(body: str, async_client: AsyncClient, logged_in_token: str) -> dict:
    # Send a POST request to the "/post" endpoint with the given post content
    response = await async_client.post("/post", json={"body": body},
                                       headers={"Authorization": f"Bearer {logged_in_token}"})
    # Return the JSON response from the server, which includes the post details
    return response.json()


# Function to create a new comment by sending an HTTP POST request to the "/comment" endpoint
async def create_comment(body: str, post_id: int, async_client: AsyncClient, logged_in_token: str) -> dict:
    # Send a POST request to the "/comment" endpoint with the given comment content and post ID
    response = await async_client.post(
        "/comment", json={"body": body, "post_id": post_id}, headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    # Return the JSON response from the server, which includes the comment details
    return response.json()


async def like_post(
        post_id: int, async_client: AsyncClient, logged_in_token: str) -> dict:
    response = await async_client.post(
        "/like",
        json={"post_id": post_id},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    return response.json()


# Fixture to create a post before each test
@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    # Use the create_post function to create a post with the body "Test Post"
    return await create_post("Test Post", async_client, logged_in_token)


# Fixture to create a comment before each test
@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict, logged_in_token: str):
    # Use the create_comment function to create a comment for the previously created post
    return await create_comment("Test Comment", created_post["id"], async_client, logged_in_token)


# Test to check if a post can be created successfully
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_create_post(async_client: AsyncClient, confirmed_user: dict, logged_in_token: str):
    body = "Test Post"
    # Send a POST request to create a new post with the specified body content
    response = await async_client.post(
        "/post",
        json={"body": body}, headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    # Assert that the response status code is 201 (Created), indicating success
    assert response.status_code == 201
    # Assert that the response contains the correct post data
    assert {"id": 1, "body": body, "user_id": confirmed_user["id"],
            "image_url": None, }.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_expired_token(
        async_client: AsyncClient, confirmed_user: dict, mocker):
    mocker.patch("storeapi.security.access_token_expire_minutes", return_value=-1)
    token = security.create_access_token(confirmed_user["email"])
    response = await async_client.post(
        "/post",
        json={"body": "Test Post"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]


# Test to check the behavior when creating a post with missing data
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_create_post_missing_data(async_client: AsyncClient, logged_in_token: str):
    # Send a POST request to create a new post with no data
    response = await async_client.post("/post", json={}, headers={"Authorization": f"Bearer {logged_in_token}"})
    # Assert that the response status code is 422 (Unprocessable Entity), indicating a validation error
    assert response.status_code == 422


@pytest.mark.anyio
async def test_like_post(
        async_client: AsyncClient, created_post: dict, logged_in_token: str
):
    response = await async_client.post(
        "/like",
        json={"post_id": created_post["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 201


# Test to check if all posts can be retrieved
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    # Send a GET request to retrieve all posts
    response = await async_client.get("/post")
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200
    # Assert that the response JSON matches the created post
    # assert response.json() == [{**created_post, "likes": 0}]
    assert created_post.items() <= response.json()[0].items()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "sorting, expected_orders",
    [
        ("new", [2, 1]),
        ("old", [1, 2]),
    ]
)
async def test_get_all_posts_sorting(
        async_client: AsyncClient,
        logged_in_token: str,
        sorting: str,
        expected_orders: list[int]
):
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    response = await async_client.get("/post", params={"sorting": sorting})
    assert response.status_code == 200
    data = response.json()

    post_ids = [post["id"] for post in data]
    assert post_ids == expected_orders


@pytest.mark.anyio
async def test_get_all_posts_sort_likes(
        async_client: AsyncClient,
        logged_in_token: str
):
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    await like_post(1, async_client, logged_in_token)
    response = await async_client.get("/post", params={"sorting": "most_likes"})
    assert response.status_code == 200
    data = response.json()
    expected_order = [2, 1]
    post_ids = [post["id"] for post in data]
    expected_order = [1, 2]
    assert post_ids == expected_order


@pytest.mark.anyio
async def test_get_all_posts_wrong_sorting(async_client: AsyncClient):
    response = await async_client.get("/post", params={"sorting": "wrong"})
    assert response.status_code == 422


# Test to check if a comment can be created successfully
@pytest.mark.anyio  # Marks this test as an async test using the anyio plugin
async def test_create_comment(async_client: AsyncClient, created_post: dict, confirmed_user: dict,
                              logged_in_token: str):
    body = "Test Comment"
    # Send a POST request to create a new comment on the specified post
    response = await async_client.post(
        "/comment",
        json={"body": body, "post_id": created_post["id"]},
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    # Assert that the response status code is 201 (Created), indicating success
    assert response.status_code == 201
    # Assert that the response contains the correct comment data
    assert {
               "id": 1,
               "body": body,
               "post_id": created_post["id"],
               "user_id": confirmed_user["id"],
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
        "post": {**created_post, "likes": 0},
        "comments": [created_comment],
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
