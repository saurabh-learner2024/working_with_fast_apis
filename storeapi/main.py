import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from storeapi.database import database
from storeapi.logging_conf import configure_logging
from storeapi.routers.post import router as post_router

logger = logging.getLogger(__name__)

# A context manager is basically a function that does some setup and some teardown. And in middle it pauses execution
# until something happens
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Hello World")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

# app.include_router(post_router, prefix="/posts")
app.include_router(post_router)
