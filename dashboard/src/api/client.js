import axios from "axios";

const API_BASE = "https://f1-strategy-intelligence-production.up.railway.app";

export const predictPit = async (lapData) => {
  const response = await axios.post(`${API_BASE}/predict`, lapData);
  return response.data;
};

export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE}/health`);
  return response.data;
};