"""
Persistent user profile storage for preference learning and mood history.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

PROFILE_PATH = Path(__file__).resolve().parent / "user_profiles.json"


def _read_all() -> dict[str, Any]:
    if not PROFILE_PATH.exists():
        return {}
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _write_all(data: dict[str, Any]) -> None:
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _default_profile() -> dict[str, Any]:
    return {
        "genre_weights": {},
        "liked_movies": [],
        "disliked_movies": [],
        "emotion_history": [],
    }


def get_profile(user_id: int) -> dict[str, Any]:
    data = _read_all()
    key = str(int(user_id))
    profile = data.get(key) or _default_profile()
    for k, v in _default_profile().items():
        profile.setdefault(k, v)
    return profile


def save_profile(user_id: int, profile: dict[str, Any]) -> None:
    data = _read_all()
    data[str(int(user_id))] = profile
    _write_all(data)


def add_emotion_event(user_id: int, dominant_emotion: str) -> dict[str, Any]:
    profile = get_profile(user_id)
    history = profile.get("emotion_history", [])
    history.append(
        {
            "emotion": str(dominant_emotion).lower(),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
    )
    profile["emotion_history"] = history[-10:]
    save_profile(user_id, profile)
    return profile


def register_feedback(user_id: int, movie_id: int, genres: list[str], liked: bool) -> dict[str, Any]:
    profile = get_profile(user_id)
    liked_movies = set(int(x) for x in profile.get("liked_movies", []))
    disliked_movies = set(int(x) for x in profile.get("disliked_movies", []))
    genre_weights: dict[str, float] = {
        str(k): float(v) for k, v in profile.get("genre_weights", {}).items()
    }

    movie_id = int(movie_id)
    step = 0.25 if liked else -0.30
    for genre in genres:
        genre_weights[genre] = float(genre_weights.get(genre, 0.0)) + step

    if liked:
        liked_movies.add(movie_id)
        disliked_movies.discard(movie_id)
    else:
        disliked_movies.add(movie_id)
        liked_movies.discard(movie_id)

    profile["genre_weights"] = genre_weights
    profile["liked_movies"] = sorted(liked_movies)
    profile["disliked_movies"] = sorted(disliked_movies)
    save_profile(user_id, profile)
    return profile


def mood_trend(history: list[dict[str, Any]]) -> str:
    if not history:
        return "unknown"
    emotions = [str(row.get("emotion", "")).lower() for row in history][-10:]
    stress_set = {"angry", "fear", "sad", "disgust"}
    positive_set = {"happy", "surprise"}
    stress_count = sum(1 for e in emotions if e in stress_set)
    positive_count = sum(1 for e in emotions if e in positive_set)
    if stress_count >= 6:
        return "stressed"
    if positive_count >= 6:
        return "improving"
    return "stable"
