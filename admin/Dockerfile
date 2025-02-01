FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a symbolic link to the backend models
RUN mkdir -p /app/backend/app/models && \
    ln -s /app/backend/app/models /app/models

# Set environment variable for better Python output
ENV PYTHONUNBUFFERED=1

# Command to run the CLI
CMD ["python", "cli.py"]
