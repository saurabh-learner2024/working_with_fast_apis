from fastapi import FastAPI
from storeapi.models.post import UserPost, UserPostIn

app = FastAPI()


# Async in-front of a function just means that this function can run more or less at the same time as other
# functions. If any of the function that we are trying to run at the same time do heavy computation then they
# can't run at the same time but if they are all just waiting for the client to send some data or they
# are waiting for the database to respond our request or things like that then those functions can run
# in parallel more or less.So that is where we get a speed benefit when we use fastapi and async function
@app.get("/")
async def root():
    return {"message": "Hello World"}




post_table = {}


@app.post("/", response_model=UserPost)
async def create_post(post: UserPostIn):
    data = post.dict()
    last_record_id = len(post_table)
    new_post = {**data, "id": last_record_id}
    post_table[last_record_id] = new_post
    return new_post

@app.get("/post", response_model=list[UserPost])
async def get_all_posts():
    return list(post_table.values())