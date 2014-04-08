#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MIN_EXECUTION_TIME 1
#define MAX_EXECUTION_TIME 4
#define PROBABILITY_FAILURE 1
#define PROBABILITY_RUNS 4

int main(int argc, char *argv[]) {
    // random vars to simulate real conditions
    int execution_time = 0;
    int return_status = 0;

    int return_status_temp = 0;

    // init rand with the random device (/dev/urandom)
    // not using /dev/random because reading it can be slow
    // see: http://stackoverflow.com/a/11990066/2530295
    //      http://superuser.com/questions/359599/why-is-my-dev-random-so-slow-when-using-dd
    unsigned int seed_int = 0;
    FILE *file = NULL;
    if (! (file = fopen("/dev/urandom", "r"))) { // open /dev/urandom
        printf("Error while opening /dev/urandom\n");
    }
    fread((char*)(&seed_int), sizeof(seed_int), 1, file); // read a random seed
    fclose(file);
    srand(seed_int); // init rand with seed

    // generate execution time: MIN_EXECUTION_TIME <= execution_time <= MAX_EXECUTION_TIME
    execution_time = (rand() % (MAX_EXECUTION_TIME - MIN_EXECUTION_TIME + 1)) +
            MIN_EXECUTION_TIME;
    // generate return status
    // 0 <= return_status_temp <= PROBABILITY_RUNS - 1
    return_status_temp = rand() % PROBABILITY_RUNS;
    // return_status_temp < PROBABILITY_FAILURE => failure
    if (return_status_temp < PROBABILITY_FAILURE) {
        return_status = EXIT_FAILURE;
    } else {
        return_status = EXIT_SUCCESS;
    }   

    // simulate the program execution time 
    sleep(execution_time);
    // simulate a program which sometimes fail
    return return_status;
}
