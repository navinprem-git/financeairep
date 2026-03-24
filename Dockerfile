# Use a lightweight Python image for faster cold starts on Azure
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for certain PDF and AI libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
# This makes subsequent builds much faster
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Healthcheck: Tells Azure if the container is actually running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
# We use --server.address=0.0.0.0 so Azure can route traffic to it
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
