# ── Stage 1: build dependencies ──────────────────────────────────────────
# Using a slim Python image keeps the final image small
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into a separate layer so Docker can cache them.
# Only re-runs when requirements.txt changes, not on every code change.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY main.py .

# Don't run as root — principle of least privilege
RUN useradd -m appuser
USER appuser

# Expose the port Uvicorn will listen on
EXPOSE 8000

# Start the server. $PORT is set by Railway/Render automatically.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
