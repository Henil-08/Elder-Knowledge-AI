FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (only FFmpeg is needed)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first
COPY requirements.txt .

# Install Python libraries
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Tell Cloud Run what command to run when the container starts
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--timeout", "0", "main:app", "--bind", "0.0.0.0:8080"]