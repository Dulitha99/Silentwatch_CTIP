FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if required for psycopg2 or other python packages
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY collectors/requirements.txt ./collectors/requirements.txt
RUN pip install --no-cache-dir -r collectors/requirements.txt

# Copy the entire app
COPY . /app/

# Expose the webhook listener port
EXPOSE 8001

CMD ["python", "webhook_listener.py"]
