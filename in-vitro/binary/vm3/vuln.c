#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void pop_rdi_gadget() {
    asm("pop %rdi; ret");
}

void vuln(void) {
    char buf[64];
    puts("Tell me something! (Don't worry, my buffer is totally trustworthy)");
    puts("What could possibly go wrong?");
    read(STDIN_FILENO, buf, 0x200);
    printf("You said: %s\n", buf);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    puts("=======================");
    puts("Welcome to 'rop-me'!");
    puts("Your mission: read /flag.txt --> Your weapon: questionable C code.");
    puts("Here we go...");
    puts("=======================");
    sleep(2);
    vuln();
    return 0;
}