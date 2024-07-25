import logging
from fastapi import APIRouter, HTTPException
from storeapi.database import comment_table, post_table, database
from storeapi.models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments

# An API router is basically a fastapi app but instead of running on its own it can be included be included into an existing app.
# Then it basically lets you see these endpoints in the original app
router = APIRouter()

logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"Finding post with id of {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)


# Async in-front of a function just means that this function can run more or less at the same time as other
# functions. If any of the function that we are trying to run at the same time do heavy computation then they
# can't run at the same time but if they are all just waiting for the client to send some data or they
# are waiting for the database to respond our request or things like that then those functions can run
# in parallel more or less.So that is where we get a speed benefit when we use fastapi and async function
@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    logger.info("Creating Post")
    data = post.model_dump()
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    logger.info("Creating comment")
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    data = comment.model_dump()
    query = comment_table.insert().values(data)
    logger.debug(query, extra={"email": "saurabh.jaiswal@net"})
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    logger.info("Getting comment on post")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info("Getting post and its comments")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post, "comments": await get_comments_on_post(post_id),
    }

# await simply make sure that this function gets called and finishes running before continuing the execution of the current line
# of code here. Remember that these async functions can sometimes be run in parallel but in this specific case you want to
# actually wait for it to finish
