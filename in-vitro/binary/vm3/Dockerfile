FROM debian:bookworm
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc socat libc6-dev && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -U -s /bin/bash ctf

WORKDIR /home/ctf

COPY vuln.c /home/ctf/vuln.c
COPY flag.txt /home/flag.txt
COPY /libc/libc.so.6 /home/ctf/libc/libc.so.6
COPY /libc/ld-linux-x86-64.so.2 /home/ctf/libc/ld-linux-x86-64.so.2


RUN gcc -no-pie /home/ctf/vuln.c -o /usr/local/bin/vuln && \
    chown root:ctf /usr/local/bin/vuln && chmod 750 /usr/local/bin/vuln && \
    chown ctf:ctf /home/flag.txt && chmod 400 /home/flag.txt

USER ctf
WORKDIR /home

EXPOSE 9003

CMD socat -T 60 TCP-LISTEN:9003,reuseaddr,fork \
    EXEC:"/home/ctf/libc/ld-linux-x86-64.so.2 --library-path /home/ctf/libc /usr/local/bin/vuln",pty,ctty,raw,echo=0,stderr,setsid,sigint