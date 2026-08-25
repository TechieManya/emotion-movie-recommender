import { useEffect, useState } from "react";
import { addToWatchlist, fetchMovies, sendFeedback, surprise } from "../services/api";
import MovieCard from "../components/MovieCard";
import MovieModal from "../components/MovieModal";

export default function HomePage() {
  const [movies, setMovies] = useState([]);
  const [surpriseRows, setSurpriseRows] = useState([]);
  const [surpriseLoading, setSurpriseLoading] = useState(false);
  const [surpriseError, setSurpriseError] = useState("");
  const [selectedMovie, setSelectedMovie] = useState(null);
  const userId = localStorage.getItem("user") || "guest";

  useEffect(() => {
    fetchMovies()
      .then((rows) => setMovies(rows.slice(0, 18)))
      .catch(() => setMovies([]));
  }, []);

  const onAddWatchlist = async (movie) => {
    try { await addToWatchlist(userId, movie); } catch (e) { console.error(e); }
  };
  const onLike = async (movie) => {
    try { await sendFeedback(userId, movie.title, "like"); } catch (e) { console.error(e); }
  };
  const onDislike = async (movie) => {
    try { await sendFeedback(userId, movie.title, "dislike"); } catch (e) { console.error(e); }
  };

  const loadSurprise = async () => {
    setSurpriseLoading(true);
    setSurpriseError("");
    setSurpriseRows([]);
    try {
      const rows = await surprise(userId);
      if (!rows || rows.length === 0) {
        setSurpriseError("No surprise movies returned. Try again!");
      } else {
        setSurpriseRows(rows);
      }
    } catch (err) {
      console.error("Surprise error:", err);
      setSurpriseError("Failed to load surprise movies. Make sure backend is running.");
    } finally {
      setSurpriseLoading(false);
    }
  };

  return (
    <div className="page">
      <section className="hero-banner">
        <h1>What should you watch when your emotions decide for you?</h1>
        <p>AI reads your mood and recommends the right stories.</p>
        <button className="primary-btn" onClick={loadSurprise} disabled={surpriseLoading}>
          {surpriseLoading ? "Finding picks..." : "🎯 Surprise Me"}
        </button>
        {surpriseError && (
          <p style={{ color: "#ff6b6b", marginTop: "0.75rem" }}>{surpriseError}</p>
        )}
      </section>

      <section>
        <h2>Trending Movies</h2>
        <div className="movie-grid">
          {movies.slice(0, 6).map((m) => (
            <MovieCard
              key={`t-${m.movie_id}`}
              movie={m}
              onSelect={setSelectedMovie}
              onAddWatchlist={onAddWatchlist}
              onLike={onLike}
              onDislike={onDislike}
            />
          ))}
        </div>
      </section>

      <section>
        <h2>Recommended For You</h2>
        <div className="movie-grid">
          {movies.slice(6, 12).map((m) => (
            <MovieCard
              key={`r-${m.movie_id}`}
              movie={m}
              onSelect={setSelectedMovie}
              onAddWatchlist={onAddWatchlist}
              onLike={onLike}
              onDislike={onDislike}
            />
          ))}
        </div>
      </section>

      <section>
        <h2>Based On Mood</h2>
        <div className="movie-grid">
          {movies.slice(12, 18).map((m) => (
            <MovieCard
              key={`m-${m.movie_id}`}
              movie={m}
              onSelect={setSelectedMovie}
              onAddWatchlist={onAddWatchlist}
              onLike={onLike}
              onDislike={onDislike}
            />
          ))}
        </div>
      </section>

      {surpriseRows.length > 0 && (
        <section>
          <h2>🎯 Surprise Picks</h2>
          <div className="movie-grid">
            {surpriseRows.map((m, idx) => (
              <MovieCard
                key={`s-${m.movie_id || idx}`}
                movie={m}
                onSelect={setSelectedMovie}
                onAddWatchlist={onAddWatchlist}
                onLike={onLike}
                onDislike={onDislike}
              />
            ))}
          </div>
        </section>
      )}

      <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
    </div>
  );
}
