import { useEffect, useState } from "react";
import MovieCard from "../components/MovieCard";
import MovieModal from "../components/MovieModal";
import { addToWatchlist, recommend, sendFeedback } from "../services/api";

const MODES = ["Emotion Mode", "Comfort Mode", "Trending Mode"];

export default function RecommendationPage() {
  const [mode, setMode] = useState("Emotion Mode");
  const [mood, setMood] = useState("happy");
  const [genres, setGenres] = useState("Comedy,Animation");
  const [query, setQuery] = useState("");
  const [rows, setRows] = useState([]);
  const [generalRows, setGeneralRows] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const userId = localStorage.getItem("user") || "guest";

  useEffect(() => {
    const last = localStorage.getItem("lastEmotion");
    if (!last) return;
    try {
      const parsed = JSON.parse(last);
      if (parsed.mood) setMood(parsed.mood);
      if (Array.isArray(parsed.genres) && parsed.genres.length > 0) {
        setGenres(parsed.genres.join(","));
      }
    } catch (_e) {
      // ignore parse errors
    }
  }, []);

  const getRecommendations = async () => {
    setLoading(true);
    setError("");
    setRows([]);
    setGeneralRows([]);
    try {
      const payload = {
        user_id: userId,
        mode,
        mood,
        genres: genres
          .split(",")
          .map((g) => g.trim())
          .filter(Boolean),
        query,
        liked_movies: [],
        top_n: 10,
      };
      const data = await recommend(payload);
      setRows(data.recommendations || []);
      setGeneralRows(data.general_recommendations || []);
      if ((data.recommendations || []).length === 0 && (data.general_recommendations || []).length === 0) {
        setError("No recommendations found. Try changing mood or genres.");
      }
    } catch (err) {
      console.error("Recommend error:", err);
      setError("Failed to get recommendations. Make sure the backend is running on http://127.0.0.1:8000");
    } finally {
      setLoading(false);
    }
  };

  const onAddWatchlist = async (movie) => {
    try { await addToWatchlist(userId, movie); } catch (e) { console.error(e); }
  };
  const onLike = async (movie) => {
    try { await sendFeedback(userId, movie.title, "like"); } catch (e) { console.error(e); }
  };
  const onDislike = async (movie) => {
    try { await sendFeedback(userId, movie.title, "dislike"); } catch (e) { console.error(e); }
  };

  return (
    <div className="page">
      <h2>Recommendations</h2>
      <div className="filters">
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          {MODES.map((m) => (
            <option value={m} key={m}>
              {m}
            </option>
          ))}
        </select>
        <input
          value={mood}
          onChange={(e) => setMood(e.target.value)}
          placeholder="Mood e.g. happy, sad, angry"
        />
        <input
          value={genres}
          onChange={(e) => setGenres(e.target.value)}
          placeholder="Genres e.g. Comedy,Drama"
        />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='Query e.g. "good movies"'
        />
        <button onClick={getRecommendations} className="primary-btn" disabled={loading}>
          {loading ? "Loading..." : "Get Recommendations"}
        </button>
      </div>

      {error && <p style={{ color: "#ff6b6b", marginTop: "1rem" }}>{error}</p>}
      {loading && <p style={{ color: "#aaa", marginTop: "1rem" }}>Fetching recommendations...</p>}

      {rows.length > 0 && (
        <>
          <h3>Emotion / Profile Based Results</h3>
          <div className="movie-grid">
            {rows.map((m, idx) => (
              <MovieCard
                key={`r-${m.movie_id || idx}`}
                movie={m}
                onSelect={setSelectedMovie}
                onAddWatchlist={onAddWatchlist}
                onLike={onLike}
                onDislike={onDislike}
              />
            ))}
          </div>
        </>
      )}

      {generalRows.length > 0 && (
        <>
          <h3>General Recommendations</h3>
          <div className="movie-grid">
            {generalRows.map((m, idx) => (
              <MovieCard
                key={`g-${idx}`}
                movie={m}
                onSelect={setSelectedMovie}
                onAddWatchlist={onAddWatchlist}
                onLike={onLike}
                onDislike={onDislike}
              />
            ))}
          </div>
        </>
      )}

      <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
    </div>
  );
}
