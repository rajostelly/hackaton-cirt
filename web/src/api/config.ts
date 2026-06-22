// Base de l'API. En dev, "/api" est proxifié vers le backend (vite.config.ts).
// En prod, on injecte VITE_API_BASE_URL au build (ex. http://serveur:8000).
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";
