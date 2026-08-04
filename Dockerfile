FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Set environment variable defaults
ENV POSTGRES_URI=sqlite:///./ekos_production.db
ENV PORT=8000

# Run FastAPI using uvicorn
CMD ["python", "-m", "backend.main"]
