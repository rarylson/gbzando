#include <stdio.h>
#include "lcg.h"

#define SEEDS 3
#define SEED_1 3
#define SEED_2 7
#define SEED_3 9
#define NUMS 20

int main(int argc, char *argv[]) {
    int seeds[SEEDS] = {SEED_1, SEED_2, SEED_3};
    int i = 0;
    int j = 0;

    for (i = 0; i < SEEDS; i++) {
        lcg_seed(seeds[i]);
        printf("Random numbers (seed %d): ", seeds[i]);
        for (j = 0; j < NUMS; j++) {
            printf("%u", lcg_rand());
            if (j != NUMS -1) {
                printf(", ");
            }
        }
        printf("\n");
    }
}
