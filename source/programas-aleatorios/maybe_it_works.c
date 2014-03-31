#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>    

#define MIN_EXECUTION_TIME 1
#define MAX_EXECUTION_TIME 4
#define PROBABILITY_FAILURE 1
#define PROBABILITY_RUNS 4

int main(int argc, char *argv[]) {
    // random vars to simulate real conditions
    int execution_time = 0;
    int return_status = 0;

    float probability = 0;
    float rand_float = 0;

    srand(time(NULL)); // init rand with a pseudorandom seed

    // generate execution time: MIN_EXECUTION_TIME <= execution_time <= MAX_EXECUTION_TIME
    execution_time = (rand() % (MAX_EXECUTION_TIME - MIN_EXECUTION_TIME + 1)) +
            MIN_EXECUTION_TIME;
    // generate return status
    probability = (float)(PROBABILITY_FAILURE) / PROBABILITY_RUNS;
    rand_float = (float)(rand()) / RAND_MAX; // random number in [0,1]
    if (rand_float < probability) {
        return_status = EXIT_FAILURE;
    } else {
        return_status = EXIT_SUCCESS;
    }
    
    // simulate the program execution time 
    sleep(execution_time);
    // simulate a program which sometimes fail
    return return_status;
}
