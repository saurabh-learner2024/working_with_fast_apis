from contextlib import asynccontextmanager
from fastapi import FastAPI
from storeapi.database import database
from storeapi.routers.post import router as post_router

# A context manager is basically a function that does some setup and some teardown. And in middle it pauses execution
# until something happens
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# app.include_router(post_router, prefix="/posts")
app.include_router(post_router)