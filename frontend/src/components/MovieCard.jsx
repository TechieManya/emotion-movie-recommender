export default function MovieCard({ movie, onSelect, onAddWatchlist, onLike, onDislike }) {
  const title = movie.title || "Untitled";
  const rating = movie.predicted_rating 
    ? `${movie.predicted_rating.toFixed(2)} / 5` 
    : (movie.rating || "N/A");
  const poster = movie.poster_url;
  const overview = movie.description || movie.overview || "No description available";

  // Safe score display — surprise/chat movies don't have emotion_score etc.
  const why =
    movie.final_score != null && movie.emotion_score != null
      ? `Emotion ${movie.emotion_score.toFixed(2)} | Pref ${
          movie.preference_score?.toFixed(2) ?? "?"
        } | Trend ${movie.trending_score?.toFixed(2) ?? "?"}`
      : movie.reason || "Recommended for you";

  return (
    <article className="movie-card clickable" onClick={() => onSelect?.(movie)}>
      <div className="poster-wrap">
        <img
          className="poster-img"
          src={poster}
          alt={title}
          onError={(e) => {
            if (
              movie.fallback_poster_url &&
              e.currentTarget.src !== movie.fallback_poster_url
            ) {
              e.currentTarget.src = movie.fallback_poster_url;
            }
          }}
        />
        <div className="poster-overlay">
          <p>{overview.length > 120 ? `${overview.slice(0, 120)}...` : overview}</p>
          <div className="actions">
            <button
              className="ghost-btn"
              onClick={(e) => {
                e.stopPropagation();
                window.open(
                  movie.trailer_url ||
                    `https://www.youtube.com/results?search_query=${encodeURIComponent(
                      title + " trailer"
                    )}`,
                  "_blank"
                );
              }}
            >
              Watch Trailer
            </button>
          </div>
        </div>
      </div>
      <h4>{title}</h4>
      <p>Rating: {rating}</p>
      <p className="why">{why}</p>
      <div className="card-actions">
        <button
          className="ghost-btn tiny-btn"
          onClick={(e) => {
            e.stopPropagation();
            onAddWatchlist?.(movie);
            const btn = e.currentTarget;
            btn.textContent = "✅";
            setTimeout(() => (btn.textContent = "❤️"), 1500);
          }}
          title="Add to watchlist"
        >
          ❤️
        </button>
        <button
          className="ghost-btn tiny-btn"
          onClick={(e) => {
            e.stopPropagation();
            onLike?.(movie);
            const btn = e.currentTarget;
            btn.textContent = "✅";
            setTimeout(() => (btn.textContent = "👍"), 1500);
          }}
          title="Like"
        >
          👍
        </button>
        <button
          className="ghost-btn tiny-btn"
          onClick={(e) => {
            e.stopPropagation();
            onDislike?.(movie);
            const btn = e.currentTarget;
            btn.textContent = "✅";
            setTimeout(() => (btn.textContent = "👎"), 1500);
          }}
          title="Dislike"
        >
          👎
        </button>
      </div>
    </article>
  );
}
