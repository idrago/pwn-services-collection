#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main() {
    char buffer[64];  

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin,  NULL, _IONBF, 0);

    puts("Welcome! \n I'll tell you where my buffer is. It's not like anybody can write in assembly, right?");
    printf("Buffer address: %p\n", (void*)buffer);
    puts("plz don't hack me :(");

    read(0, buffer, 256); 

    
    return 0;
}