"""
Load Surprise SVD model and MovieLens 100k items; recommend by mood genres.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = BASE_DIR / "svd_model.pkl"
DEFAULT_ITEM_PATH = BASE_DIR / "ml-100k" / "u.item"
DEFAULT_RATINGS_PATH = BASE_DIR / "ml-100k" / "u.data"

ITEM_COLUMNS = [
    "movie_id",
    "title",
    "release_date",
    "video_release_date",
    "imdb_url",
    "unknown",
    "Action",
    "Adventure",
    "Animation",
    "Children's",
    "Comedy",
    "Crime",
    "Documentary",
    "Drama",
    "Fantasy",
    "Film-Noir",
    "Horror",
    "Musical",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "War",
    "Western",
]

GENRE_COLUMNS = ITEM_COLUMNS[5:]


def load_movies_df(item_path: Path | None = None) -> pd.DataFrame:
    path = item_path or DEFAULT_ITEM_PATH
    df = pd.read_csv(
        path,
        sep="|",
        names=ITEM_COLUMNS,
        encoding="latin-1",
        engine="python",
    )
    for col in GENRE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["movie_id"] = pd.to_numeric(df["movie_id"], errors="coerce").astype(int)
    return df


def load_popularity_df(ratings_path: Path | None = None) -> pd.DataFrame:
    path = ratings_path or DEFAULT_RATINGS_PATH
    ratings = pd.read_csv(
        path,
        sep="\t",
        names=["user_id", "movie_id", "rating", "timestamp"],
        engine="python",
    )
    grp = (
        ratings.groupby("movie_id", as_index=False)
        .agg(rating_count=("rating", "count"), avg_rating=("rating", "mean"))
    )
    max_count = float(grp["rating_count"].max() or 1.0)
    grp["trending_score"] = (
        0.6 * (grp["rating_count"] / max_count) + 0.4 * (grp["avg_rating"] / 5.0)
    )
    return grp[["movie_id", "avg_rating","trending_score"]]


def load_svd_model(model_path: Path | None = None):
    path = model_path or DEFAULT_MODEL_PATH
    with open(path, "rb") as f:
        return pickle.load(f)


def load_model_and_catalog(
    model_path: Path | None = None,
    item_path: Path | None = None,
) -> tuple[object, pd.DataFrame, pd.DataFrame]:
    """Single entry for caching: model + movie table + popularity table."""
    return load_svd_model(model_path), load_movies_df(item_path), load_popularity_df()


def recommend_top_movies(
    user_id: int,
    genres: list[str],
    model,
    movies_df: pd.DataFrame,
    top_n: int = 10,
) -> list[tuple[str, float]]:
    """
    Predict ratings for every movie, then keep rows matching any requested genre, return top_n (title, rating).
    """
    if not genres:
        return []

    genres_set = {g for g in genres if g in movies_df.columns}
    if not genres_set:
        return []

    uid = int(user_id)
    work = movies_df.copy()
    work["predicted_rating"] = work["movie_id"].apply(
        lambda mid: float(model.predict(uid, int(mid)).est)
    )

    mask = False
    for g in genres_set:
        mask = mask | (work[g] == 1)
    work = work.loc[mask]
    if work.empty:
        return []

    work = work.sort_values("predicted_rating", ascending=False).head(top_n)
    return [(str(t), float(r)) for t, r in zip(work["title"], work["predicted_rating"])]


def hybrid_recommendations(
    user_id: int,
    genres: list[str],
    model,
    movies_df: pd.DataFrame,
    popularity_df: pd.DataFrame,
    profile: dict[str, Any] | None = None,
    mode: str = "Emotion Mode",
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Weighted score:
      final = 0.5 emotion + 0.3 preference + 0.2 trending  (mode-dependent tweaks)
    Returns columns including score breakdown for explainability.
    """
    genres = [g for g in genres if g in movies_df.columns]
    if not genres:
        return pd.DataFrame()
    profile = profile or {}
    genre_weights = {k: float(v) for k, v in profile.get("genre_weights", {}).items()}
    liked = set(int(x) for x in profile.get("liked_movies", []))
    disliked = set(int(x) for x in profile.get("disliked_movies", []))

    work = movies_df.copy()
    uid = int(user_id)
    work["predicted_rating"] = work["movie_id"].apply(lambda m: float(model.predict(uid, int(m)).est))
    work["pred_norm"] = (work["predicted_rating"] / 5.0).clip(0.0, 1.0)

    matched_count = 0
    for g in genres:
        matched_count = matched_count + work[g]
    work = work.loc[matched_count > 0].copy()
    if work.empty:
        return pd.DataFrame()

    max_match = float(len(genres))
    work["emotion_score"] = (matched_count.loc[work.index] / max_match).clip(0.0, 1.0)

    def _pref_score(row: pd.Series) -> float:
        movie_id = int(row["movie_id"])
        if movie_id in disliked:
            return 0.0
        base = 0.5
        if movie_id in liked:
            base += 0.2
        boost = 0.0
        for g in GENRE_COLUMNS:
            if int(row[g]) == 1:
                boost += float(genre_weights.get(g, 0.0))
        return float(min(1.0, max(0.0, base + boost * 0.08)))

    work["preference_score"] = work.apply(_pref_score, axis=1)

    work = work.merge(popularity_df, on="movie_id", how="left")
    work["trending_score"] = work["trending_score"].fillna(0.25).clip(0.0, 1.0)

    if mode == "Trending Mode":
        w_emotion, w_pref, w_trending = 0.30, 0.20, 0.50
    elif mode == "Comfort Mode":
        w_emotion, w_pref, w_trending = 0.55, 0.35, 0.10
    elif mode == "Surprise Me Mode":
        w_emotion, w_pref, w_trending = 0.40, 0.20, 0.40
    elif mode == "Deep Mood Mode":
        w_emotion, w_pref, w_trending = 0.60, 0.30, 0.10
    else:
        w_emotion, w_pref, w_trending = 0.50, 0.30, 0.20

    work["final_score"] = (
        w_emotion * work["emotion_score"]
        + w_pref * work["preference_score"]
        + w_trending * work["trending_score"]
    )

    if mode == "Surprise Me Mode":
        work["final_score"] = work["final_score"] + (1.0 - work["emotion_score"]) * 0.08

    work = work.sort_values(["final_score", "predicted_rating"], ascending=False).head(top_n)
    return work[
        [
            "movie_id",
            "title",
            "predicted_rating",
            "emotion_score",
            "preference_score",
            "trending_score",
            "final_score",
        ]
    ].reset_index(drop=True)
