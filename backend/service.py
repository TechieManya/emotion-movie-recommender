from __future__ import annotations

import base64
import random
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import cv2
import numpy as np

import profile_store
import recommender

BASE_DIR = Path(__file__).resolve().parent.parent

_MODEL = None
_MOVIES_DF = None
_POPULARITY_DF = None
_DETAILS_CACHE: dict[str, dict[str, Any]] = {}

_DETAILS_CACHE: dict[str, dict[str, Any]] = {}



KNOWN_DESCRIPTIONS: dict[str, str] = {
    "toy story": "A cowboy doll is threatened when a new spaceman toy becomes the child's favorite.",
    "fargo": "A dark crime thriller about a kidnapping gone wrong in Minnesota.",
    "the godfather": "The rise and fall of a powerful Italian-American mafia family.",
    "pulp fiction": "Interconnected crime stories told in a nonlinear style.",
    "the silence of the lambs": "An FBI trainee seeks help from a cannibalistic serial killer to catch another killer.",
    "forrest gump": "The extraordinary life of a simple man from Alabama who witnesses historical events.",
    "the shawshank redemption": "Two imprisoned men bond over years, finding solace and redemption through acts of decency.",
    "schindler's list": "A German businessman saves over a thousand Jewish lives during the Holocaust.",
    "the matrix": "A hacker discovers a mind-blowing truth about reality and joins a war against its controllers.",
    "inception": "A thief who enters dreams is given the task of planting an idea in someone's mind.",
    "interstellar": "A team of explorers travel through a wormhole in space to ensure humanity's survival.",
    "the dark knight": "Batman faces the Joker, a criminal mastermind who wants to plunge Gotham into anarchy.",
    "goodfellas": "The story of Henry Hill and his life in the mob from childhood to adulthood.",
    "fight club": "An insomniac office worker forms an underground fight club with a soap salesman.",
    "titanic": "A romance between a poor artist and a rich woman aboard the ill-fated RMS Titanic.",
    "jurassic park": "A theme park showcasing real dinosaurs turns dangerous when the animals escape.",
    "goldeneye": "James Bond must prevent a criminal syndicate from using a satellite weapon.",
    "casino": "The story of a mob man running a Las Vegas casino in the 1970s.",
    "heat": "A seasoned detective and a skilled thief clash in a tense cat-and-mouse thriller.",
    "babe": "A little pig who wants to be a sheepdog achieves his dream with determination.",
    "twelve monkeys": "A convict travels back in time to gather information about a deadly plague.",
    "get shorty": "A Miami loan shark goes to Hollywood and finds that the movie business is similar to his own.",
    "se7en": "Two detectives hunt a serial killer who uses the seven deadly sins as his motives.",
    "braveheart": "Scottish warrior William Wallace leads his countrymen in a rebellion against English rule.",
    "the usual suspects": "A sole survivor tells of the twists and his encounters with a mysterious criminal.",
    "the fugitive": "A man wrongly convicted of his wife's murder escapes and tries to find the real killer.",
    "the lion king": "A young lion prince flees his kingdom after the murder of his father.",
    "aladdin": "A kind-hearted street urchin and a power-hungry Grand Vizier compete for a magic lamp.",
    "beauty and the beast": "A prince cursed to live as a beast can only be freed by true love.",
    "home alone": "A boy is left home alone and must defend his house against burglars.",
    "speed": "A bomb on a bus will explode if it slows below 50mph.",
    "jumanji": "Two siblings get sucked into a board game that brings jungle dangers into the real world.",
    "avatar": "A marine on an alien planet is torn between duty and protecting the world he calls home.",
    "gladiator": "A Roman general is betrayed and his family murdered, forcing him to become a gladiator.",
    "the departed": "An undercover cop and a mole in the police attempt to identify each other.",
    "no country for old men": "Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong.",
    "american beauty": "A man in a mid-life crisis has a life-changing encounter with his daughter's friend.",
    "iron man": "Billionaire inventor Tony Stark builds a powered suit of armor and becomes a superhero.",
    "the avengers": "Earth's mightiest heroes must come together to stop Loki and his alien army.",
}

GENERAL_POPULAR_PICKS: list[dict[str, Any]] = [
    {"title": "The Shawshank Redemption", "reason": "General Recommendation: critically acclaimed classic"},
    {"title": "The Godfather", "reason": "General Recommendation: iconic high-quality cinema"},
    {"title": "The Dark Knight", "reason": "General Recommendation: universally loved blockbuster"},
    {"title": "Forrest Gump", "reason": "General Recommendation: uplifting and widely appreciated"},
    {"title": "Inception", "reason": "General Recommendation: smart and engaging mainstream favorite"},
]

EMOTION_TO_GENRES = {
    "happy": ["Comedy", "Animation"],
    "sad": ["Drama", "Romance"],
    "angry": ["Action", "Thriller"],
    "fear": ["Horror", "Mystery"],
    "surprise": ["Sci-Fi", "Adventure"],
    "neutral": ["Documentary", "Drama"],
    "disgust": ["Crime", "Thriller"],
}


def _numeric_user_id(user_id: str | int) -> int:
    try:
        n = int(user_id)
        if 1 <= n <= 943:
            return n
    except (TypeError, ValueError):
        pass
    return (abs(hash(str(user_id))) % 943) + 1


def _imdb_search_url(title: str) -> str:
    return f"https://www.imdb.com/find?q={quote_plus(title)}"


def _youtube_trailer_url(title: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(title + ' official trailer')}"


def clean_title(title: str) -> str:
    return re.sub(r"\(\d{4}\)", "", str(title or "")).strip()


def _normalize_title(title: str) -> str:
    clean = str(title or "").strip()
    if "(" in clean:
        clean = clean.split("(", 1)[0].strip()
    return clean


def get_poster_url(title: str) -> str:
    """Returns a dynamic backend URL that will fetch the poster from IMDb API."""
    key = clean_title(title).lower().strip()
    return f"http://127.0.0.1:8000/poster/{quote_plus(key)}"


def _local_poster_data_uri(title: str) -> str:
    cleaned = clean_title(title) or "Movie Poster"
    safe = cleaned[:28].replace("&", "and").replace("<", "").replace(">", "")
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='300' height='450'>
  <defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
    <stop offset='0%' stop-color='#1a2045'/><stop offset='100%' stop-color='#2b1f5e'/>
  </linearGradient></defs>
  <rect width='100%' height='100%' fill='url(#g)'/>
  <rect x='18' y='18' width='264' height='414' rx='14' fill='none' stroke='#6573d4' stroke-width='2'/>
  <text x='50%' y='47%' text-anchor='middle' fill='#e6e8ff' font-size='18' font-family='Arial'>MOVIE</text>
  <text x='50%' y='56%' text-anchor='middle' fill='#e6e8ff' font-size='14' font-family='Arial'>{safe}</text>
</svg>""".strip()
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def generate_description(title: str, genres: list[str]) -> str:
    cleaned = clean_title(title)
    key = cleaned.lower()
    if key in KNOWN_DESCRIPTIONS:
        return KNOWN_DESCRIPTIONS[key]
    if genres:
        return f"{cleaned} is a {', '.join(genres)} movie recommended based on your mood and preferences."
    return f"{cleaned} is a recommended movie based on your preferences."


def get_movie_details(title: str, genres: list[str] | None = None) -> dict[str, Any]:
    """Get movie details with ZERO network calls."""
    genres = genres or []
    clean = _normalize_title(title)
    key = clean_title(clean).lower()
    cache_key = f"{key}|{','.join(sorted(genres))}"

    if cache_key in _DETAILS_CACHE:
        return _DETAILS_CACHE[cache_key]

    description = generate_description(clean, genres)

    details = {
        "poster_url": get_poster_url(clean),
        "fallback_poster_url": _local_poster_data_uri(clean),
        "backdrop_url": "",
        "overview": description,
        "description": description,
        "rating": None,
        "release_date": "",
        "imdb_url": _imdb_search_url(clean),
        "trailer_url": _youtube_trailer_url(clean),
    }
    _DETAILS_CACHE[cache_key] = details
    return details


def _genres_for_movie_id(movie_id: int) -> list[str]:
    _, movies_df, _ = init_assets()
    row_df = movies_df.loc[movies_df["movie_id"] == int(movie_id)]
    if row_df.empty:
        return []
    row = row_df.iloc[0]
    return [g for g in recommender.GENRE_COLUMNS if int(row[g]) == 1]


def genres_for_title(movie_title: str) -> list[str]:
    _, movies_df, _ = init_assets()
    target = clean_title(movie_title).lower()
    for _, row in movies_df.iterrows():
        if clean_title(str(row["title"])).lower() == target:
            return [g for g in recommender.GENRE_COLUMNS if int(row[g]) == 1]
    return []


def init_assets() -> tuple[Any, Any, Any]:
    global _MODEL, _MOVIES_DF, _POPULARITY_DF
    if _MODEL is None or _MOVIES_DF is None or _POPULARITY_DF is None:
        _MODEL, _MOVIES_DF, _POPULARITY_DF = recommender.load_model_and_catalog()
    return _MODEL, _MOVIES_DF, _POPULARITY_DF


def decode_image_base64(image_base64: str) -> np.ndarray:
    payload = image_base64.split(",", 1)[1] if "," in image_base64 else image_base64
    binary = base64.b64decode(payload)
    np_buf = np.frombuffer(binary, dtype=np.uint8)
    frame = cv2.imdecode(np_buf, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Invalid image payload.")
    return frame


def _rows_to_api(rows) -> list[dict[str, Any]]:
    _, _, popularity_df = init_assets()
    out = []
    for _, row in rows.iterrows():
        movie_id = int(row["movie_id"])
        title = str(row["title"])
        genres = _genres_for_movie_id(movie_id)
        details = get_movie_details(title, genres).copy()
        
        pop_row = popularity_df.loc[popularity_df["movie_id"] == movie_id]
        if not pop_row.empty and "avg_rating" in popularity_df.columns:
            details["rating"] = f"{float(pop_row.iloc[0]['avg_rating']):.2f} / 5"

        out.append({
            "movie_id": movie_id,
            "title": title,
            "predicted_rating": float(row["predicted_rating"]),
            "emotion_score": float(row["emotion_score"]),
            "preference_score": float(row["preference_score"]),
            "trending_score": float(row["trending_score"]),
            "final_score": float(row["final_score"]),
            "genres": genres,
            **details,
        })
    return out


def recommend_for_user(
    user_id: int,
    genres: list[str],
    mode: str,
    mood: str | None = None,
    liked_movies: list[int] | None = None,
    query: str | None = None,
    top_n: int = 10,
) -> dict[str, Any]:
    numeric_user_id = _numeric_user_id(user_id)
    model, movies_df, popularity_df = init_assets()
    profile = profile_store.get_profile(numeric_user_id)
    if liked_movies:
        merged = sorted(
            set(int(x) for x in profile.get("liked_movies", [])).union(int(x) for x in liked_movies)
        )
        profile["liked_movies"] = merged
        profile_store.save_profile(numeric_user_id, profile)

    if (not genres) and mood:
        genres = EMOTION_TO_GENRES.get(str(mood).strip().lower(), EMOTION_TO_GENRES["neutral"])

    rec_df = recommender.hybrid_recommendations(
        user_id=numeric_user_id,
        genres=genres,
        model=model,
        movies_df=movies_df,
        popularity_df=popularity_df,
        profile=profile,
        mode=mode,
        top_n=top_n,
    )
    results = _rows_to_api(rec_df) if len(rec_df) > 0 else []

    general_queries = {"good movies", "top movies", "suggest something interesting", "suggest", "recommend"}
    q = (query or "").strip().lower()
    use_general = any(token in q for token in general_queries) if q else False

    general_picks: list[dict[str, Any]] = []
    if use_general:
        for row in GENERAL_POPULAR_PICKS[:5]:
            details = get_movie_details(row["title"], [])
            general_picks.append({"title": row["title"], "genres": [], "reason": row["reason"], **details})

    return {"recommendations": results, "general_recommendations": general_picks}


def analyze_frame_and_recommend(user_id: int, image_base64: str, mode: str = "Emotion Mode") -> dict[str, Any]:
    import mood_detector

    numeric_user_id = _numeric_user_id(user_id)
    frame = decode_image_base64(image_base64)
    mood_result = mood_detector.analyze_bgr_frame(frame)
    if not mood_result.get("ok"):
        return {
            "emotion": "unknown",
            "mood": "unknown",
            "emotion_scores": {},
            "genres": [],
            "recommendations": [],
            "error": mood_result.get("error", "Emotion analysis failed."),
        }

    dominant = str(mood_result.get("dominant_emotion", "neutral"))
    profile_store.add_emotion_event(numeric_user_id, dominant)
    rec = recommend_for_user(
        user_id=numeric_user_id,
        genres=mood_result.get("genres", []),
        mode=mode,
        mood=mood_result.get("mood"),
        top_n=10,
    )
    return {
        "emotion": dominant,
        "mood": mood_result.get("mood"),
        "emotion_scores": mood_result.get("emotion_scores", {}),
        "genres": mood_result.get("genres", []),
        "recommendations": rec["recommendations"],
        "general_recommendations": rec["general_recommendations"],
    }


def movies_catalog() -> list[dict[str, Any]]:
    """Returns full catalog. Posters are lazy-loaded via the backend proxy API."""
    _, movies_df, popularity_df = init_assets()
    out = []
    for _, row in movies_df.iterrows():
        movie_id = int(row["movie_id"])
        genres = [g for g in recommender.GENRE_COLUMNS if int(row[g]) == 1]
        title = str(row["title"])
        details = get_movie_details(title, genres).copy()
        
        # Get average rating from popularity_df
        pop_row = popularity_df.loc[popularity_df["movie_id"] == movie_id]
        if not pop_row.empty and "avg_rating" in popularity_df.columns:
            details["rating"] = f"{float(pop_row.iloc[0]['avg_rating']):.2f} / 5"
            
        out.append({
            "movie_id": movie_id,
            "title": title,
            "genres": genres,
            **details,
        })
    return out


def surprise_movies(sample_size: int = 5) -> list[dict[str, Any]]:
    """Returns random movies."""
    _, movies_df, popularity_df = init_assets()
    sample = movies_df.sample(n=min(sample_size, len(movies_df)))
    out = []
    for _, row in sample.iterrows():
        movie_id = int(row["movie_id"])
        genres = [g for g in recommender.GENRE_COLUMNS if int(row[g]) == 1]
        title = str(row["title"])
        details = get_movie_details(title, genres).copy()
        
        pop_row = popularity_df.loc[popularity_df["movie_id"] == movie_id]
        if not pop_row.empty and "avg_rating" in popularity_df.columns:
            details["rating"] = f"{float(pop_row.iloc[0]['avg_rating']):.2f} / 5"
            
        out.append({
            "movie_id": movie_id,
            "title": title,
            "genres": genres,
            **details,
        })
    return out


def chat_recommend(user_id: str | int, message: str, top_n: int = 10) -> dict[str, Any]:
    """Chat-based recommendation using message keywords."""
    msg = message.lower()
    
    # Map keywords to genres
    keyword_genre_map = {
        "funny": ["Comedy"], "comedy": ["Comedy"], "laugh": ["Comedy"],
        "scary": ["Horror"], "horror": ["Horror"], "fear": ["Horror"],
        "action": ["Action"], "fight": ["Action"], "adventure": ["Adventure"],
        "romantic": ["Romance"], "love": ["Romance"], "romance": ["Romance"],
        "thriller": ["Thriller"], "suspense": ["Thriller"],
        "drama": ["Drama"], "emotional": ["Drama"],
        "sci-fi": ["Sci-Fi"], "science fiction": ["Sci-Fi"], "space": ["Sci-Fi"],
        "animation": ["Animation"], "animated": ["Animation"],
        "documentary": ["Documentary"],
        "mystery": ["Mystery"], "crime": ["Crime"],
        "sad": ["Drama", "Romance"], "happy": ["Comedy", "Animation"],
        "exciting": ["Action", "Adventure"], "dark": ["Thriller", "Crime"],
    }
    
    genres: list[str] = []
    for kw, genre_list in keyword_genre_map.items():
        if kw in msg:
            genres.extend(genre_list)
    genres = list(set(genres))
    
    mood = None
    if "happy" in msg or "funny" in msg:
        mood = "happy"
    elif "sad" in msg:
        mood = "sad"
    elif "scary" in msg or "fear" in msg:
        mood = "fear"
    elif "angry" in msg or "action" in msg:
        mood = "angry"

    result = recommend_for_user(
        user_id=user_id,
        genres=genres,
        mode="Emotion Mode",
        mood=mood,
        top_n=top_n,
    )
    return result
