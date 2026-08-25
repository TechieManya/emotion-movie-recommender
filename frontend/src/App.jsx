import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import AuthPage from "./pages/AuthPage";
import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";
import DetectionPage from "./pages/DetectionPage";
import HomePage from "./pages/HomePage";
import RecommendationPage from "./pages/RecommendationPage";
import WatchlistPage from "./pages/WatchlistPage";

function ProtectedRoute({ children }) {
  const user = localStorage.getItem("user");
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <div>
      <Navbar />
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/detect"
          element={
            <ProtectedRoute>
              <DetectionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/recommendations"
          element={
            <ProtectedRoute>
              <RecommendationPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-list"
          element={
            <ProtectedRoute>
              <WatchlistPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}
