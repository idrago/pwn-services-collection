FROM debian:bookworm
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc socat libc6-dev && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -U -s /bin/bash ctf
WORKDIR /home/ctf

COPY vuln.c /home/ctf/vuln.c
RUN gcc -no-pie -z execstack -fno-stack-protector -D_FORTIFY_SOURCE=0 -w /home/ctf/vuln.c -o /usr/local/bin/vuln && \
    chown root:ctf /usr/local/bin/vuln && \
    chmod 750 /usr/local/bin/vuln 


COPY flag.txt /home/flag.txt
RUN chown ctf:ctf /home/flag.txt && chmod 400 /home/flag.txt

USER ctf
WORKDIR /home
EXPOSE 9000

CMD socat -T 60 TCP-LISTEN:9000,reuseaddr,fork \
    EXEC:"/usr/local/bin/vuln",pty,ctty,raw,echo=0,stderr,setsid,sigint

