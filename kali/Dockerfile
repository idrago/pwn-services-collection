FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

# Update and install all tools
RUN apt-get update && \
    apt-get install -y \
    nmap \
    netcat-traditional \
    curl \
    wget \
    dnsutils \
    gdb \
    gdb-multiarch \
    binutils \
    file \
    strace \
    ltrace \
    gcc \
    g++ \
    make \
    python3 \
    python3-pip \
    python3-dev \
    vim \
    nano \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install checksec separately (it's in a different package)
RUN apt-get update && \
    apt-get install -y checksec && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python exploitation tools
RUN pip3 install --no-cache-dir --break-system-packages \
    pwntools \
    requests \
    ROPgadget \
    capstone \
    keystone-engine \
    unicorn

# Create working directories
RUN mkdir -p /root/scripts /root/results

WORKDIR /root

# Verify installations
RUN which nmap && \
    which python3 && \
    python3 -c "import pwn" && \
    echo "All tools installed successfully"

CMD ["tail", "-f", "/dev/null"]