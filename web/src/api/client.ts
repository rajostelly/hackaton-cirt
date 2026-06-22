import axios from "axios";
import { API_BASE } from "./config";

// https://axios-http.com/docs/instance
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
