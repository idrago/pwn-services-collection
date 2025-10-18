#!/bin/bash

echo "Testing CTF Agent setup"
echo ""

# Check Docker
if ! docker --version > /dev/null 2>&1; then
    echo "FAIL: Docker not installed"
    exit 1
fi
echo "PASS: Docker installed"

# Check docker-compose
if ! docker-compose --version > /dev/null 2>&1; then
    echo "FAIL: Docker Compose not installed"
    exit 1
fi
echo "PASS: Docker Compose installed"

# Check .env
if [ ! -f .env ]; then
    echo "FAIL: .env file missing"
    exit 1
fi
echo "PASS: .env file exists"

source .env
if [ "$MODEL_NAME" = "your-model-name" ]; then
    echo "WARN: MODEL_NAME not configured in .env"
fi

# Check file structure
REQUIRED_FILES=(
    "agent/ctf_agent.py"
    "agent/Dockerfile"
    "agent/requirements.txt"
    "docker-compose.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "FAIL: Missing $file"
        exit 1
    fi
done
echo "PASS: All required files present"

# Check services
if docker-compose ps | grep -q "Up"; then
    echo "PASS: Services running"
else
    echo "WARN: Services not running (use: docker-compose up -d)"
fi

# Check API
if [ ! -z "$OPENAI_BASE_URL" ]; then
    if curl -s -f "$OPENAI_BASE_URL/models" > /dev/null 2>&1; then
        echo "PASS: API reachable"
    else
        echo "WARN: Cannot reach API at $OPENAI_BASE_URL"
    fi
fi

echo ""
echo "Setup validation complete"
