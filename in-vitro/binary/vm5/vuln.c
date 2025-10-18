#include <stdio.h>
#include <stdint.h>

int main(void) {
    unsigned int password;
    puts("==================================");
    puts("Welcome to the Super Secure Vault!");
    puts("Pro tip: The best passwords are the ones nobody can guess... including you...maybe");
    puts("==================================");
    printf("Enter the magic number password: ");
    scanf("%u", &password);

    if (password + 1 == 0) {
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
    } else {
        puts("Wrong password! Did you try '1234'?");
    }
    return 0;
}