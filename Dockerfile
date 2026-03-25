# ─── Stage 1: Build Frontend ──────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /build-frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Backend Builder ─────────────────────────────────
FROM python:3.11-slim AS backend-builder
WORKDIR /build-backend
RUN apt-get update && apt-get install -y --no-install-recommends gcc libgomp1 && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ─── Stage 3: Runtime ─────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 curl && rm -rf /var/lib/apt/lists/*

# Copy backend environment from builder
COPY --from=backend-builder /install /usr/local

# Copy frontend build to backend static folder
COPY --from=frontend-builder /build-frontend/dist /app/static

# Copy backend code
COPY backend/main.py backend/demo_data.json ./
COPY backend/model /app/model

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
# Note: Render provides the PORT env var. We use it if available, defaulting to 8000.
# Use JSON format for compatibility and better signal handling
CMD ["python", "main.py"]
