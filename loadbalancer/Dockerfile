FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create directory for config file
RUN mkdir -p /config

# Set environment variables
ENV PORT=8082
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8082

# Run the application
CMD ["python", "app.py"]
