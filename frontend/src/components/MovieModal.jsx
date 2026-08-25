export default function MovieModal({ movie, onClose }) {
  if (!movie) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          x
        </button>
        <div className="modal-content">
          <img
            src={movie.poster_url}
            alt={movie.title}
            className="modal-poster"
            onError={(e) => {
              if (movie.fallback_poster_url && e.currentTarget.src !== movie.fallback_poster_url) {
                e.currentTarget.src = movie.fallback_poster_url;
              }
            }}
          />
          <div>
            <h2>{movie.title}</h2>
            <p><b>Rating:</b> {movie.rating ?? movie.predicted_rating?.toFixed?.(2) ?? "N/A"}</p>
            <p><b>Genres:</b> {movie.genres?.join?.(", ") || "N/A"}</p>
            <p>{movie.description || movie.overview || "No description available"}</p>
            <div className="actions">
              <button className="primary-btn" onClick={() => window.open(movie.imdb_url, "_blank")}>
                View on IMDb
              </button>
              <button className="ghost-btn" onClick={() => window.open(movie.trailer_url, "_blank")}>
                Watch Trailer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
