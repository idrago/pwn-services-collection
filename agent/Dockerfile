FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory with proper permissions
RUN mkdir -p /app/output && chmod 777 /app/output

# Copy agent code and configuration
COPY ctf_agent.py .
COPY config.yaml .

# Keep container running
CMD ["tail", "-f", "/dev/null"]