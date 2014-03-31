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

    int return_status_temp = 0;

    // init rand with a seed
    unsigned int seed_int = (unsigned int)time(NULL); // default value
    if (argc > 1) {
        seed_int = (unsigned int)atol(argv[1]); // reading from command line args
    }
    srand(seed_int);

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
