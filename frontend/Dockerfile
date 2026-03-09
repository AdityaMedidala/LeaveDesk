# ── Stage 1: build the Vue app ───────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (cached layer)
COPY package*.json ./
RUN npm install --silent

# Copy source and build
COPY . .
RUN npm run build
# Output: /app/dist


# ── Stage 2: serve with nginx ─────────────────────────────────────────────
# nginx:alpine is ~25MB — much smaller than a Node runtime
FROM nginx:alpine

# Copy built files into nginx's serve directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config to handle Vue Router (HTML5 history mode)
# Without this, refreshing on /employee returns a 404
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
