# Compiler and flags
CC = gcc
CFLAGS = -no-pie -z execstack -fno-stack-protector -D_FORTIFY_SOURCE=0 -w -fpermissive -Wno-error -Wno-implicit-function-declaration -Wno-return-mismatch
TARGET = vuln
SOURCE = vuln.c

# Default target
all: $(TARGET)

# Build the vulnerable binary
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) $(SOURCE) -o $(TARGET)
	@echo "Built $(TARGET)"

# Clean build artifacts
clean:
	rm -f $(TARGET)
	@echo "Cleaned build artifacts"

# Run the program
run: $(TARGET)
	./$(TARGET)

# Test the exploit 
exploit: $(TARGET)
	@if [ -f exploit.py ]; then \
		echo "Running exploit..."; \
		python3 exploit.py; \
	else \
		echo "exploit.py not found"; \
	fi

# Build Docker container
docker-build:
	docker build -t vm2-challenge .

# Run Docker container
docker-run: docker-build
	docker run -p 9002:9002 vm2-challenge

# Stop Docker container
docker-stop:
	docker stop $$(docker ps -q --filter "ancestor=vm2-challenge")

.PHONY: all clean run exploit docker-build docker-run docker-stop
