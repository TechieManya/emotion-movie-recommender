from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend import auth_store, service, user_features_store
from backend.schemas import (
    AnalyzeFrameRequest,
    AuthRequest,
    ChatRecommendRequest,
    FeedbackRequest,
    RecommendRequest,
    SurpriseRequest,
    WatchlistAddRequest,
    WatchlistRemoveRequest,
)

import requests
import urllib.parse
from fastapi.responses import RedirectResponse

app = FastAPI(title="Emotion Movie API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    service.init_assets()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/signup")
def signup(payload: AuthRequest) -> dict[str, str]:
    ok, msg = auth_store.signup(payload.username, payload.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}


@app.post("/login")
def login(payload: AuthRequest) -> dict[str, str]:
    ok, msg = auth_store.login(payload.username, payload.password)
    if not ok:
        raise HTTPException(status_code=401, detail=msg)
    return {"message": msg}


@app.get("/movies")
def movies() -> dict[str, object]:
    return {"movies": service.movies_catalog()}


@app.post("/recommend")
def recommend(payload: RecommendRequest) -> dict[str, object]:
    rec = service.recommend_for_user(
        user_id=payload.user_id,
        genres=payload.genres,
        mode=payload.mode,
        mood=payload.mood,
        liked_movies=payload.liked_movies,
        query=payload.query,
        top_n=payload.top_n,
    )
    prefs = user_features_store.get_preferences(payload.user_id)
    disliked = set(prefs.get("disliked", []))
    liked = set(prefs.get("liked", []))
    liked_genres = prefs.get("liked_genres", {})

    filtered = []
    for row in rec.get("recommendations", []):
        if row.get("title") in disliked:
            continue
        score = float(row.get("final_score", 0.0))
        if row.get("title") in liked:
            score += 0.20
        for g in row.get("genres", []):
            score += 0.03 * float(liked_genres.get(g, 0))
        row["personalized_score"] = score
        filtered.append(row)
    filtered.sort(key=lambda x: float(x.get("personalized_score", x.get("final_score", 0))), reverse=True)
    rec["recommendations"] = filtered
    return rec


@app.post("/analyze-frame")
def analyze_frame(payload: AnalyzeFrameRequest) -> dict[str, object]:
    if not payload.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required.")
    return service.analyze_frame_and_recommend(
        user_id=payload.user_id,
        image_base64=payload.image_base64,
        mode=payload.mode,
    )


@app.post("/watchlist/add")
def watchlist_add(payload: WatchlistAddRequest) -> dict[str, object]:
    items = user_features_store.add_to_watchlist(payload.user_id, payload.movie)
    return {"watchlist": items}


@app.get("/watchlist")
def watchlist_get(user_id: str | int) -> dict[str, object]:
    return {"watchlist": user_features_store.get_watchlist(user_id)}


@app.delete("/watchlist/remove")
def watchlist_remove(payload: WatchlistRemoveRequest) -> dict[str, object]:
    items = user_features_store.remove_from_watchlist(payload.user_id, payload.movie_title)
    return {"watchlist": items}


@app.post("/feedback")
def feedback(payload: FeedbackRequest) -> dict[str, object]:
    action = payload.action.strip().lower()
    if action not in {"like", "dislike"}:
        raise HTTPException(status_code=400, detail="action must be 'like' or 'dislike'")
    genres = service.genres_for_title(payload.movie_title)
    prefs = user_features_store.apply_feedback(payload.user_id, payload.movie_title, action, genres)
    return {"preferences": prefs}


@app.post("/surprise")
def surprise(payload: SurpriseRequest) -> dict[str, object]:
    return {"movies": service.surprise_movies(sample_size=5)}


@app.post("/chat-recommend")
def chat_recommend(payload: ChatRecommendRequest) -> dict[str, object]:
    msg = payload.message.lower()
    genre_map = {
        "funny": "Comedy",
        "scary": "Horror",
        "romantic": "Romance",
        "action": "Action",
        "sad": "Drama",
    }
    mood_words = {"happy", "sad", "angry", "fear", "surprise", "neutral", "disgust"}
    genres = [g for k, g in genre_map.items() if k in msg]
    mood = next((m for m in mood_words if m in msg), None)
    rec = service.recommend_for_user(
        user_id=payload.user_id,
        genres=genres,
        mode="Emotion Mode",
        mood=mood,
        query=payload.message,
        top_n=payload.top_n,
    )
    prefs = user_features_store.get_preferences(payload.user_id)
    disliked = set(prefs.get("disliked", []))
    rec["recommendations"] = [r for r in rec.get("recommendations", []) if r.get("title") not in disliked]
    return rec


@app.get("/poster/{title}")
def get_poster(title: str):
    """Dynamically fetch the poster from IMDb suggestion API (no key required, highly available)."""
    clean = title.strip()
    seed = abs(hash(clean)) % 1000
    fallback = f"https://picsum.photos/seed/movie{seed}/300/450"
    if not clean:
        return RedirectResponse(fallback)

    try:
        # IMDb's autocomplete suggestion API is incredibly reliable for posters
        letter = clean[0].lower()
        if not letter.isalnum():
            letter = "a"
        url = f"https://v3.sg.media-imdb.com/suggestion/{letter}/{urllib.parse.quote(clean.lower())}.json"
        
        # simple HTTP request
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("d", []):
                image_url = item.get("i", {}).get("imageUrl")
                if image_url:
                    return RedirectResponse(image_url)
    except Exception:
        pass
        
    return RedirectResponse(fallback)
