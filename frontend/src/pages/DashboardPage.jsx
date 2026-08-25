import { useMemo } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function DashboardPage() {
  const lastEmotion = useMemo(() => {
    const data = localStorage.getItem("lastEmotion");
    if (!data) return null;
    try {
      return JSON.parse(data);
    } catch (_e) {
      return null;
    }
  }, []);

  const chartData = lastEmotion?.emotion_scores
    ? Object.entries(lastEmotion.emotion_scores).map(([emotion, value]) => ({ emotion, value }))
    : [];

  return (
    <div className="page">
      <h2>Dashboard</h2>
      <div className="dashboard-grid">
        <div className="panel-card">
          <h3>Latest Emotion Snapshot</h3>
          {lastEmotion ? (
            <>
              <p>Emotion: {lastEmotion.emotion}</p>
              <p>Mood: {lastEmotion.mood}</p>
              <p>Genres: {lastEmotion.genres?.join(", ")}</p>
            </>
          ) : (
            <p>No emotion data available.</p>
          )}
        </div>
        <div className="panel-card">
          <h3>Emotion Confidence Chart</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData}>
              <XAxis dataKey="emotion" stroke="#d6dbff" />
              <YAxis stroke="#d6dbff" />
              <Tooltip />
              <Bar dataKey="value" fill="#8d5bff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
