#include <stdio.h>
#include <stdlib.h>
#include <string.h>


void win() {
    puts("Congratulations! You've found the flag!");
    FILE *f = fopen("flag.txt", "r");
        if (!f) {
            puts("flag missing");
            return 1;
        }
        char buf[128];
        fgets(buf, sizeof(buf), f);
        puts("Here's your flag:");
        puts(buf);
        fclose(f);
}

void vulnerable() {
    char buffer[64];
    puts("Enter input:");
    gets(buffer);
}
void banner() {
    puts("Welcome to the easiest pwn challenge ever!");
    
}
int main() {
    banner();
    vulnerable();
    return 0;
}
