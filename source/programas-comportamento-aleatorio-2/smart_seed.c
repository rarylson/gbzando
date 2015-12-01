#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define DEBUG 0
#define DEBUG_SEED 99
#define NUMS 10
#define NUM_MAX 100

int main(int argc, char *argv[]) {
    int i = 0;

    // if debug, use a well-known seed
    if (DEBUG) {
        srand(DEBUG_SEED);
    // else, use the system time as seed
    } else {
        srand(time(NULL));
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
