import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, signup } from "../services/api";

export default function AuthPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    try {
      const fn = isSignup ? signup : login;
      await fn(username, password);
      localStorage.setItem("user", username);
      navigate("/");
    } catch (err) {
      setMessage(
        err?.response?.data?.detail ||
          "Authentication failed. If backend is starting, wait 20-30s and try again."
      );
    }
  };

  const continueAsGuest = () => {
    localStorage.setItem("user", "demo_guest");
    navigate("/");
  };

  return (
    <div className="center-page">
      <form className="auth-card" onSubmit={submit}>
        <h2>{isSignup ? "Sign Up" : "Login"}</h2>
        <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username" required />
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          placeholder="Password"
          required
        />
        <button type="submit" className="primary-btn">
          {isSignup ? "Create Account" : "Login"}
        </button>
        <button type="button" className="ghost-btn" onClick={() => setIsSignup((v) => !v)}>
          {isSignup ? "Already have an account? Login" : "New user? Sign up"}
        </button>
        <button type="button" className="ghost-btn" onClick={continueAsGuest}>
          Continue as Guest (Submission Mode)
        </button>
        {message && <p className="error">{message}</p>}
      </form>
    </div>
  );
}
