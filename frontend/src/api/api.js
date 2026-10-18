import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://voicedocai-api.onrender.com",
});

export default API;
