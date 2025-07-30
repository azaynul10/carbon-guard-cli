# Example Dockerfile for optimization testing
FROM ubuntu:latest

# Install system dependencies
RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get install -y git

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Create user
RUN useradd -m appuser

# Switch to user
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["python3", "app.py"]
