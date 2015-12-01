#include <stdio.h>
#include <stdlib.h>

#define DEBUG 0
#define DEBUG_SEED 99
#define NUMS 10
#define NUM_MAX 100

// returns a random number from /dev/urandom
// based on: http://stackoverflow.com/a/11990066/2530295
unsigned long int get_urandom(void) {
    unsigned long int urandom = 0;
    FILE *f = NULL;

    // open /dev/urandom
    if (! (f = fopen("/dev/urandom", "r"))) {
        printf("Error while opening /dev/urandom\n");
    }
    // read an 'unsigned long int' from /dev/urandom
    fread((char*)(&urandom), sizeof(urandom), 1, f);
    fclose(f);

    return urandom;
}

int main(int argc, char *argv[]) {
    int i = 0;

    // if debug, use a well-known seed
    if (DEBUG) {
        srand(DEBUG_SEED);
    // else, use a good seed
    } else {
        srand(get_urandom());
    }

    printf("Random numbers: ");
    for (i = 0; i < NUMS; i++) {
        printf("%u", rand() % NUM_MAX);
        if (i != NUMS -1) {
            printf(", ");
        }
    }
    printf("\n");
}
