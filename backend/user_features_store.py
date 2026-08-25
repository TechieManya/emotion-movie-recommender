from __future__ import annotations

from collections import defaultdict
from typing import Any

user_watchlists: dict[str, list[dict[str, Any]]] = defaultdict(list)
user_preferences: dict[str, dict[str, Any]] = defaultdict(
    lambda: {"liked": [], "disliked": [], "liked_genres": {}}
)


def _key(user_id: str | int) -> str:
    return str(user_id)


def add_to_watchlist(user_id: str | int, movie: dict[str, Any]) -> list[dict[str, Any]]:
    key = _key(user_id)
    title = str(movie.get("title", "")).strip().lower()
    if not title:
        return user_watchlists[key]
    exists = any(str(m.get("title", "")).strip().lower() == title for m in user_watchlists[key])
    if not exists:
        user_watchlists[key].append(movie)
    return user_watchlists[key]


def get_watchlist(user_id: str | int) -> list[dict[str, Any]]:
    return user_watchlists[_key(user_id)]


def remove_from_watchlist(user_id: str | int, movie_title: str) -> list[dict[str, Any]]:
    key = _key(user_id)
    target = str(movie_title or "").strip().lower()
    user_watchlists[key] = [
        m for m in user_watchlists[key] if str(m.get("title", "")).strip().lower() != target
    ]
    return user_watchlists[key]


def apply_feedback(
    user_id: str | int,
    movie_title: str,
    action: str,
    genres: list[str] | None = None,
) -> dict[str, Any]:
    key = _key(user_id)
    prefs = user_preferences[key]
    title = str(movie_title or "").strip()
    if not title:
        return prefs
    liked = set(prefs.get("liked", []))
    disliked = set(prefs.get("disliked", []))
    liked_genres = dict(prefs.get("liked_genres", {}))
    genres = genres or []

    if action == "like":
        liked.add(title)
        disliked.discard(title)
        for g in genres:
            liked_genres[g] = int(liked_genres.get(g, 0)) + 1
    elif action == "dislike":
        disliked.add(title)
        liked.discard(title)
        for g in genres:
            liked_genres[g] = int(liked_genres.get(g, 0)) - 1

    prefs["liked"] = sorted(liked)
    prefs["disliked"] = sorted(disliked)
    prefs["liked_genres"] = liked_genres
    user_preferences[key] = prefs
    return prefs


def get_preferences(user_id: str | int) -> dict[str, Any]:
    return user_preferences[_key(user_id)]
