#!/bin/bash

set -e

if [ -z "$1" ]; then
    echo "Usage: ./run.sh <challenges.json>"
    exit 1
fi

CHALLENGES_FILE="$1"

if [ ! -f "$CHALLENGES_FILE" ]; then
    echo "Error: File not found: $CHALLENGES_FILE"
    exit 1
fi

# Check if services are running
if ! docker ps | grep -q ctf_agent; then
    echo "Starting services..."
    docker-compose up -d
    echo "Waiting for services to initialize..."
    sleep 10
fi

# Copy challenges to agent
docker cp "$CHALLENGES_FILE" ctf_agent:/app/challenges.json

# Run agent
docker exec -it ctf_agent python ctf_agent.py /app/challenges.json

# Copy results back
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "./agent/output/$TIMESTAMP"
docker cp ctf_agent:/app/output/. "./agent/output/"

echo ""
echo "Results saved to ./agent/output/"
