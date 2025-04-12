# Base image
FROM python:3.10-slim 

# Set working directory
WORKDIR /app

# Copy app code...
COPY api/app/ /app


# Update pip and install dependencies with verbosity
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --verbose


# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]
