
# Use official Python image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the controller script
COPY configmap_watcher.py .

# Command to run the controller
CMD ["python", "configmap_watcher.py"]
