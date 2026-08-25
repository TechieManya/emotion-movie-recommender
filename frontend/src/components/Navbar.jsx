import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const user = localStorage.getItem("user");

  const logout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav className="nav">
      <div className="brand">
        <div className="brand-name">MoodMatch</div>
        <div className="brand-tagline">Movies that match your mood.</div>
      </div>
      <div className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/detect">Emotion Detection</Link>
        <Link to="/recommendations">Recommendations</Link>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/my-list">My List</Link>
        <Link to="/chat">Chat</Link>
      </div>
      {user ? (
        <button onClick={logout} className="ghost-btn">
          Logout
        </button>
      ) : (
        <Link to="/login" className="ghost-btn">
          Login
        </Link>
      )}
    </nav>
  );
}
