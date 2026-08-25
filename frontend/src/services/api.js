import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_BASE,
});

export async function signup(username, password) {
  const { data } = await api.post("/signup", { username, password });
  return data;
}

export async function login(username, password) {
  const { data } = await api.post("/login", { username, password });
  return data;
}

export async function fetchMovies() {
  const { data } = await api.get("/movies");
  return data.movies;
}

export async function analyzeFrame(payload) {
  const { data } = await api.post("/analyze-frame", payload);
  return data;
}

export async function recommend(payload) {
  const { data } = await api.post("/recommend", payload);
  return data;
}

export async function addToWatchlist(user_id, movie) {
  const { data } = await api.post("/watchlist/add", { user_id, movie });
  return data.watchlist || [];
}

export async function getWatchlist(user_id) {
  const { data } = await api.get("/watchlist", { params: { user_id } });
  return data.watchlist || [];
}

export async function removeFromWatchlist(user_id, movie_title) {
  const { data } = await api.delete("/watchlist/remove", { data: { user_id, movie_title } });
  return data.watchlist || [];
}

export async function sendFeedback(user_id, movie_title, action) {
  const { data } = await api.post("/feedback", { user_id, movie_title, action });
  return data;
}

export async function surprise(user_id) {
  const { data } = await api.post("/surprise", { user_id });
  return data.movies || [];
}

export async function chatRecommend(user_id, message, top_n = 10) {
  const { data } = await api.post("/chat-recommend", { user_id, message, top_n });
  return data;
}
