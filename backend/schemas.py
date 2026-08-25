from __future__ import annotations
 
from typing import Any, Union
 
from pydantic import BaseModel, Field
 
 
class AnalyzeFrameRequest(BaseModel):
    user_id: Union[str, int] = 1
    image_base64: str | None = None
    mode: str = "Emotion Mode"
 
 
class RecommendRequest(BaseModel):
    user_id: Union[str, int] = 1
    genres: list[str] = Field(default_factory=list)
    mood: str | None = None
    liked_movies: list[int] = Field(default_factory=list)
    mode: str = "Emotion Mode"
    query: str | None = None
    top_n: int = 10
 
 
class AuthRequest(BaseModel):
    username: str
    password: str
 
 
class WatchlistAddRequest(BaseModel):
    user_id: Union[str, int]
    movie: dict[str, Any]
 
 
class WatchlistRemoveRequest(BaseModel):
    user_id: Union[str, int]
    movie_title: str
 
 
class FeedbackRequest(BaseModel):
    user_id: Union[str, int]
    movie_title: str
    action: str
 
 
class SurpriseRequest(BaseModel):
    user_id: Union[str, int]
 
 
class ChatRecommendRequest(BaseModel):
    user_id: Union[str, int]
    message: str
    top_n: int = 10
 
 
class ApiResponse(BaseModel):
    data: dict[str, Any]