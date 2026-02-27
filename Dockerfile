FROM python:3.11-slim

WORKDIR /app

# Recommended runtime settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    postgresql-client \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Ensure the src layout is discoverable
ENV PYTHONPATH=/app/src

# Default command is neutral; docker-compose will override for pipeline/dashboard
CMD ["python", "-c", "print('StoryLens container ready. Use docker compose to run pipeline or dashboard.')"]
