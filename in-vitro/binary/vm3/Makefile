# Compiler and flags
CC = gcc
CFLAGS = -no-pie -z execstack -fno-stack-protector -D_FORTIFY_SOURCE=0 -w -fpermissive -Wno-error -Wno-implicit-function-declaration -Wno-return-mismatch
TARGET = vuln
SOURCE = vuln.c

# Custom libc paths
LIBC_DIR = ./libc
LIBC_PATH = $(LIBC_DIR)/libc.so.6
LD_PATH = $(LIBC_DIR)/ld-linux-x86-64.so.2

# Default target
all: $(TARGET)

# Build the vulnerable binary with custom libc
$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -Wl,--rpath=$(LIBC_DIR) -Wl,--dynamic-linker=$(LD_PATH) $(SOURCE) -o $(TARGET)
	@echo "Built $(TARGET) with custom libc"

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
	docker build -t vm3-challenge .

# Run Docker container
docker-run: docker-build
	docker run -p 9003:9003 vm3-challenge

# Stop Docker container
docker-stop:
	docker stop $$(docker ps -q --filter "ancestor=vm3-challenge")

# Check which libc is being used
check-libc: $(TARGET)
	@echo "Checking libc version and path:"
	ldd $(TARGET)

.PHONY: all clean run exploit docker-build docker-run docker-stop check-libc
