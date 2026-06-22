import axios from "axios";

// https://axios-http.com/docs/instance
const apiClient = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
