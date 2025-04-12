# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy app code
COPY api/app/ .


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]
