#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>

typedef struct Game {
    void (*fn)(void);
    char payload[16];
} Game;

typedef struct Level {
    char buf[24];
} Level;

static Game *g_game;
static Level *g_level;

static void setup(void){
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    alarm(240);
}
static unsigned read_u(){
    char b[64];
    if(!fgets(b, sizeof b, stdin)) exit(0);
    return (unsigned)strtoul(b, NULL, 10);
}

static int sanitize_hex(const char *in, char *out, size_t outsz){
    size_t j=0;
    for(size_t i=0; in[i]; ++i){
        unsigned char c = (unsigned char)in[i];
        if (c=='\n' || c=='\r') break;
        if (isspace(c) || c=='_') continue;
        if (c=='0' && (in[i+1]=='x' || in[i+1]=='X')) { i++; continue; }
        if (isxdigit(c)) {
            if (j+1 < outsz) out[j++] = (char)c;
        } else {
            return 0; 
        }
    }
    out[j] = 0;
    return (j >= 1 && j <= 16);
}

__attribute__((noinline))
static void win(void){
    FILE *f=fopen("flag.txt","r");
    if(!f){ puts("flag missing"); return; }
    char b[256];
    while(fgets(b,sizeof b,f)) fputs(b,stdout);
    fclose(f);
}

void ping(void){
    puts("pong");
}

static void banner(void){
    puts("\n=======================");
    puts("Welcome to \"The game of dangling pointers\" \n Have fun!");
    puts("=======================\n");
}

static void add_game(){
    if(g_game){ puts("[!] exists"); return; }
    g_game = (Game*)malloc(sizeof(Game));
    if(!g_game) exit(1);
    g_game->fn = ping;
    puts("[game] text (<=15):");
    fgets(g_game->payload, sizeof g_game->payload, stdin);
    puts("[game] saved");
}

static void run_game(){
    if(!g_game){ puts("[!] empty"); return; }
    puts("[game] running ...");
    g_game->fn();
}

static void drop_game(){
    if(!g_game){ puts("[!] empty"); return; }
    free(g_game);                        
    puts("[game] removed");
}

static void add_level(){
    if(g_level){ puts("[!] present"); return; }
    g_level = (Level*)malloc(sizeof(Level));
    if(!g_level) exit(1);
    puts("[level] created");
}

static void edit_level(){
    if(!g_level){ puts("[!] none"); return; }
    puts("[level] content:");
    char line[128];
    if(!fgets(line, sizeof line, stdin)){ puts("[!] input"); return; }

    char hex[33]={0};
    if (sanitize_hex(line, hex, sizeof hex)) {
        unsigned long v = strtoul(hex, NULL, 16);
        memcpy(&g_level->buf[0], &v, sizeof(unsigned long));
    } else {
        memset(g_level->buf, 0, sizeof g_level->buf);
        size_t n = strcspn(line, "\r\n");
        if (n > sizeof g_level->buf) n = sizeof g_level->buf;
        memcpy(g_level->buf, line, n);
    }
    puts("[level] updated");
}

static void menu(){
    puts("1) add_game");
    puts("2) run_game");
    puts("3) drop_game");
    puts("4) add_level");
    puts("5) edit_level");
    puts("0) exit");
    printf("> ");
}

int main(){
    setup();
    banner();
    for(;;){
        menu();
        switch(read_u()){
            case 1: add_game(); break;
            case 2: run_game(); break;
            case 3: drop_game(); break;
            case 4: add_level(); break;
            case 5: edit_level(); break;
            case 0: puts("bye"); return 0;
            default: puts("?"); break;
        }
    }
}
