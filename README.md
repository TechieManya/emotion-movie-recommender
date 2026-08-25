# Emotion-Based Movie Recommendation Web App

## Backend (FastAPI)

Run from project root:

```bash
py -3.11 -m pip install -r requirements.txt
py -3.11 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Optional (for real movie posters/details from TMDb):

```bash
set TMDB_API_KEY=your_tmdb_api_key
```

If `TMDB_API_KEY` is not set or TMDb fails, backend automatically returns placeholder poster and fallback description.

API endpoints:

- `GET /health`
- `POST /signup`
- `POST /login`
- `GET /movies`
- `POST /analyze-frame`
- `POST /recommend`

## Frontend (React + Vite)

Run in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Notes

- Webcam is browser-native (`getUserMedia`) in frontend.
- Backend uses existing emotion/recommendation logic from `mood_detector.py` and `recommender.py`.
- No Streamlit UI remains.
- No OpenCV display loop (`cv2.imshow`, `cv2.waitKey`, webcam capture loop) remains.
