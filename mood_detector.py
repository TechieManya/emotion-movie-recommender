"""
Webcam mood detection: Haar face crop + DeepFace emotions, mapped to MovieLens genres.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
from deepface import DeepFace

# Dominant emotion (lowercase) -> preferred mood label + MovieLens genre names (u.item columns)
EMOTION_TO_GENRES: dict[str, tuple[str, list[str]]] = {
    "happy": ("happy", ["Comedy", "Animation"]),
    "sad": ("sad", ["Drama", "Romance"]),
    "angry": ("angry", ["Action", "Thriller"]),
    "fear": ("fear", ["Horror", "Mystery"]),
    "surprise": ("surprise", ["Sci-Fi", "Adventure"]),
    "neutral": ("neutral", ["Documentary", "Drama"]),
    "disgust": ("disgust", ["Crime", "Thriller"]),
}


def _haar_cascade() -> cv2.CascadeClassifier:
    path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    return cv2.CascadeClassifier(str(path))


def _largest_face_roi(
    gray: np.ndarray, faces: np.ndarray, frame_shape: tuple[int, int, int]
) -> tuple[int, int, int, int] | None:
    if faces is None or len(faces) == 0:
        return None
    areas = [int(w * h) for (_x, _y, w, h) in faces]
    i = int(np.argmax(areas))
    x, y, w, h = [int(v) for v in faces[i]]
    h_img, w_img = frame_shape[0], frame_shape[1]
    pad_x = int(0.15 * w)
    pad_y = int(0.15 * h)
    x0 = max(0, x - pad_x)
    y0 = max(0, y - pad_y)
    x1 = min(w_img, x + w + pad_x)
    y1 = min(h_img, y + h + pad_y)
    return x0, y0, x1 - x0, y1 - y0


def map_emotion_to_mood_and_genres(emotion_key: str) -> tuple[str, list[str]]:
    key = (emotion_key or "").strip().lower()
    if key in EMOTION_TO_GENRES:
        return EMOTION_TO_GENRES[key]
    return EMOTION_TO_GENRES["neutral"]


def _emotion_from_face(face_bgr: np.ndarray) -> dict[str, float]:
    result = DeepFace.analyze(
        img_path=face_bgr,
        actions=["emotion"],
        enforce_detection=False,
        detector_backend="skip",
        silent=True,
    )
    if isinstance(result, list):
        result = result[0]
    raw = result.get("emotion") or {}
    out: dict[str, float] = {}
    for k, v in raw.items():
        try:
            out[str(k).lower()] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def _prepare_face_variants(face_bgr: np.ndarray) -> list[np.ndarray]:
    # Ensemble from a few light-normalized variants makes webcam emotion less neutral-biased.
    base = cv2.resize(face_bgr, (224, 224), interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    eq = clahe.apply(gray)
    eq_bgr = cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)
    bright = cv2.convertScaleAbs(base, alpha=1.1, beta=12)
    return [base, eq_bgr, bright]


def analyze_bgr_frame(frame: np.ndarray) -> dict[str, Any]:
    """
    Detect face with Haar, run DeepFace emotion on the crop.
    Returns dict with ok, mood, genres, emotion_scores (0-100 floats), optional error.
    """
    if frame is None or frame.size == 0:
        return {"ok": False, "error": "Empty frame."}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cascade = _haar_cascade()
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    roi = _largest_face_roi(gray, faces, frame.shape)
    if roi is None:
        return {"ok": False, "error": "No face detected. Center your face and try again."}

    x, y, w, h = roi
    face_bgr = frame[y : y + h, x : x + w]
    if face_bgr.size == 0:
        return {"ok": False, "error": "Invalid face crop."}

    try:
        merged_scores: dict[str, float] = {}
        variants = _prepare_face_variants(face_bgr)
        for variant in variants:
            scores = _emotion_from_face(variant)
            for emo, score in scores.items():
                merged_scores[emo] = merged_scores.get(emo, 0.0) + score
        if not merged_scores:
            return {"ok": False, "error": "No emotion result returned."}
        emotion_scores = {k: v / len(variants) for k, v in merged_scores.items()}
    except Exception as exc:  # pragma: no cover - model / env specific
        return {"ok": False, "error": f"Emotion analysis failed: {exc}"}

    dominant = max(emotion_scores.items(), key=lambda x: x[1])[0]

    mood, genres = map_emotion_to_mood_and_genres(dominant)
    return {
        "ok": True,
        "mood": mood,
        "dominant_emotion": dominant,
        "genres": genres,
        "emotion_scores": emotion_scores,
    }
