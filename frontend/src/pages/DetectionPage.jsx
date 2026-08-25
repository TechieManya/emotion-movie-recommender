import { useRef, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { analyzeFrame } from "../services/api";

function frameToBase64(video) {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);
  return canvas.toDataURL("image/jpeg");
}

export default function DetectionPage() {
  const videoRef = useRef(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const startCamera = async () => {
    setError("");
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  };

  const detectEmotion = async () => {
    if (!videoRef.current || !videoRef.current.srcObject) {
      setError("Start camera first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const image_base64 = frameToBase64(videoRef.current);
      const data = await analyzeFrame({
        user_id: 1,
        image_base64,
        mode: "Emotion Mode",
      });
      setResult(data);
      localStorage.setItem("lastEmotion", JSON.stringify(data));
    } catch (e) {
      setError(e?.response?.data?.detail || "Detection failed.");
    } finally {
      setLoading(false);
    }
  };

  const chartData = result?.emotion_scores
    ? Object.entries(result.emotion_scores).map(([emotion, value]) => ({ emotion, value }))
    : [];

  return (
    <div className="page">
      <h2>Emotion Detection</h2>
      <p>Look at the camera and detect your mood directly in browser.</p>
      <div className="detect-layout">
        <div className="video-panel">
          <video ref={videoRef} autoPlay playsInline className="video-feed" />
          <div className="actions">
            <button onClick={startCamera} className="ghost-btn">
              Start Camera
            </button>
            <button onClick={detectEmotion} className="primary-btn" disabled={loading}>
              {loading ? "Detecting..." : "Detect Emotion"}
            </button>
          </div>
        </div>
        <div className="result-panel">
          {result ? (
            <>
              <h3>{result.emotion?.toUpperCase() || "UNKNOWN"}</h3>
              <p>Mood: {result.mood}</p>
              <p>Genres: {result.genres?.join(", ")}</p>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={chartData}>
                    <XAxis dataKey="emotion" stroke="#d6dbff" />
                    <YAxis stroke="#d6dbff" />
                    <Tooltip />
                    <Bar dataKey="value" fill="#6f64ff" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <p>No detection yet.</p>
          )}
          {error && <p className="error">{error}</p>}
        </div>
      </div>
    </div>
  );
}
