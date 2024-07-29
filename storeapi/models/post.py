from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserPostIn(BaseModel):
    body: str


class UserPost(UserPostIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    image_url: Optional[str] = None


class UserPostWithLikes(UserPost):
    model_config = ConfigDict(from_attributes=True)
    likes: int


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class PostLikeIn(BaseModel):
    post_id: int


class PostLike(PostLikeIn):
    id: int
    user_id: int


class UserPostWithComments(BaseModel):
    post: UserPostWithLikes
    comments: list[Comment]

# {"post": {"id": 0, "body": "My post"}, "comments": [{"id": 2, "post_id":0, "body": "My comment"}]}
