# =============================================================================
# Frontend — multi-stage: node:20-alpine build → nginx:1.27-alpine serve
# =============================================================================
FROM node:20-alpine AS build
WORKDIR /app
COPY src/frontend/package*.json ./
RUN npm install
COPY src/frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine
RUN apk add --no-cache curl
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:3000/ || exit 1
