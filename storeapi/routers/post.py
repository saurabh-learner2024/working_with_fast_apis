from fastapi import APIRouter, HTTPException
from storeapi.models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments

# An API router is basically a fastapi app but instead of running on its own it can be included be included into an existing app.
# Then it basically lets you see these endpoints in the original app
router = APIRouter()
post_table = {}
comment_table = {}


def find_post(post_id: int):
    return post_table.get(post_id)


# Async in-front of a function just means that this function can run more or less at the same time as other
# functions. If any of the function that we are trying to run at the same time do heavy computation then they
# can't run at the same time but if they are all just waiting for the client to send some data or they
# are waiting for the database to respond our request or things like that then those functions can run
# in parallel more or less.So that is where we get a speed benefit when we use fastapi and async function
@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.dict()
    last_record_id = len(post_table)
    new_post = {**data, "id": last_record_id}
    post_table[last_record_id] = new_post
    return new_post


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    return list(post_table.values())


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    post = find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    data = comment.dict()
    last_record_id = len(comment_table)
    new_comment = {**data, "id": last_record_id}
    comment_table[last_record_id] = new_comment
    return new_comment


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    return [
        comment for comment in comment_table.values() if comment["post_id"] == post_id
    ]


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post, "comments": await get_comments_on_post(post_id)
    }

# await simply make sure that this function gets called and finishes running before continuing the execution of the current line
# of code here. Remember that these async functions can sometimes be run in parallel but in this specific case you want to
# actually wait for it to finish