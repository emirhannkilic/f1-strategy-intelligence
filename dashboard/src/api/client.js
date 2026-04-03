import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export const predictPit = async (lapData) => {
  const response = await axios.post(`${API_BASE}/predict`, lapData);
  return response.data;
};

export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
};