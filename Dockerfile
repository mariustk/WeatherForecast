# Use slim Python base image
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (for better build caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of your application code
COPY . .

# Default command (overridden by docker-compose for each service)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
