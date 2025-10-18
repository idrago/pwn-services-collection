#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

char *gets(char *s); 

void win() {
    puts("I guess you really are a hacker. Well, you have my shell now!");
    fflush(stdout);
    char *args[] = {"/bin/sh",  NULL};
    execve(args[0], args, NULL);
}

int main() {
    char buffer[72];

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin,  NULL, _IONBF, 0);
    puts("Welcome! \n Before starting, I need to tell you something...");
    puts("I got weird errors when I tried to compile this program, I had to ask ChatGPT how to ignore them... \nWhat's the deal with the \"gets\" function?");
    puts("Anyways, what's your name?");

    gets(buffer);           
    printf(buffer);         

    puts(", such a beautiful name! I hope you're not a hacker... Are you?");
    
    read(0, buffer, 200);  
    puts("Thanks for your input! Bye!");
    return 0;
}
