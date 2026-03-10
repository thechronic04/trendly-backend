# --- SCALABILITY INFRASTRUCTURE: MULTI-STAGE DOCKER BUILD ---

# Stage 1: Build & Dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for PostgreSQL and ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Final Production Runtime
FROM python:3.11-slim as runtime

WORKDIR /app

# Copy the pre-installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application source code
COPY . .

# Create a non-privileged user to run the application (Security Best Practice)
RUN adduser --disabled-password --gecos '' trendly_user
USER trendly_user

# Expose API port
EXPOSE 8000

# Default Command (Overridden by Docker Compose for Workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
