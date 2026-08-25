import { useState } from "react";
import MovieCard from "../components/MovieCard";
import MovieModal from "../components/MovieModal";
import { addToWatchlist, chatRecommend, sendFeedback } from "../services/api";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedMovie, setSelectedMovie] = useState(null);
  const userId = localStorage.getItem("user") || "guest";

  const ask = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setError("");
    setRows([]);
    try {
      const data = await chatRecommend(userId, message, 10);
      const recs = data.recommendations || [];
      if (recs.length === 0) {
        setError("No movies found for that query. Try words like 'funny', 'scary', 'romantic', 'action', or 'sad'.");
      } else {
        setRows(recs);
      }
    } catch (err) {
      console.error("Chat recommend error:", err);
      setError("Something went wrong. Make sure the backend is running on http://127.0.0.1:8000");
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") ask();
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
      <h2>🤖 Chat Recommendations</h2>
      <p style={{ color: "#aaa", marginBottom: "1rem" }}>
        Describe what you want to watch. Try: <em>"funny movies"</em>, <em>"scary thriller"</em>, <em>"romantic drama"</em>
      </p>
      <div className="filters">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKey}
          placeholder='e.g. "suggest funny movies" or "I want something scary"'
          style={{ flex: 1 }}
        />
        <button className="primary-btn" onClick={ask} disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {error && (
        <p style={{ color: "#ff6b6b", marginTop: "1rem" }}>{error}</p>
      )}

      {loading && (
        <p style={{ color: "#aaa", marginTop: "1rem" }}>Finding movies for you...</p>
      )}

      {rows.length > 0 && (
        <>
          <h3 style={{ marginTop: "2rem" }}>Results</h3>
          <div className="movie-grid">
            {rows.map((m, idx) => (
              <MovieCard
                key={`chat-${m.movie_id || idx}`}
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
