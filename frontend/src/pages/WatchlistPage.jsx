import { useEffect, useState } from "react";
import MovieCard from "../components/MovieCard";
import MovieModal from "../components/MovieModal";
import { getWatchlist, removeFromWatchlist, sendFeedback } from "../services/api";

export default function WatchlistPage() {
  const [rows, setRows] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const userId = localStorage.getItem("user") || "guest";

  const load = async () => {
    const list = await getWatchlist(userId);
    setRows(list);
  };

  useEffect(() => {
    load();
  }, []);

  const onDislike = async (movie) => {
    await sendFeedback(userId, movie.title, "dislike");
    await removeFromWatchlist(userId, movie.title);
    await load();
  };

  return (
    <div className="page">
      <h2>My List</h2>
      {rows.length === 0 ? (
        <p>No movies saved yet. Add from Home or Recommendations.</p>
      ) : (
        <div className="movie-grid">
          {rows.map((m, idx) => (
            <MovieCard
              key={`wl-${m.movie_id || idx}-${m.title}`}
              movie={m}
              onSelect={setSelectedMovie}
              onDislike={onDislike}
            />
          ))}
        </div>
      )}
      <MovieModal movie={selectedMovie} onClose={() => setSelectedMovie(null)} />
    </div>
  );
}
