# Multi-stage Docker build for SwiftQueue Hospital Management System

# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build frontend
RUN npm run build

# Stage 2: Backend with Python
FROM python:3.9-slim AS backend

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (including run.py and app/)
COPY backend/ .

# Copy frontend build to static directory inside backend
COPY --from=frontend-build /app/dist ./dist

# Set environment variables
ENV SECRET_KEY=${SECRET_KEY:-changeme_generate_secure_key_in_production}
ENV DATABASE_URL=${DATABASE_URL:-sqlite:///./queue_management.db}
ENV ENVIRONMENT=${ENVIRONMENT:-production}

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["python", "run.py"]
