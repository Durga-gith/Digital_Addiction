FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Set PYTHONPATH to ensure imports work correctly
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
RUN chmod +x ./start.sh
CMD ["./start.sh"]