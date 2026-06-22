# ARO Web — React/Vite built, served by nginx
FROM node:24-alpine AS build
WORKDIR /app

# Install deps (cached unless lockfile changes)
COPY package.json package-lock.json ./
RUN npm ci

# Build the SPA
COPY . .
RUN npm run build

# ── Runtime: static files served by nginx, /api proxied to the API ──────────
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
