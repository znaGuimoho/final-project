FROM python:3.12-slim

# System deps
RUN apt update && apt install -y build-essential

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application
COPY backend/ .

# Expose port
EXPOSE 8000

# Command to run the application 
CMD ["uvicorn", "app.main:app_sio", "--host", "0.0.0.0", "--port", "8000"]
