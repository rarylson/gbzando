#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MIN_EXECUTION_TIME 1
#define MAX_EXECUTION_TIME 4
#define PROBABILITY_FAILURE 1
#define PROBABILITY_RUNS 4

// get Time Stamp Counter (TSC) in Pentium (x86 and x64). this may not work 
// with multiple processors, because there is many TSC (one in each processor)
// see: http://www.cs.wm.edu/~kearns/001lab.d/rdtsc.html
//      http://www.makelinux.net/ldd3/chp-7-sect-1
unsigned long long int rdtsc(void)
{
    unsigned long long int x;
    unsigned a, d;

    __asm__ volatile("rdtsc" : "=a" (a), "=d" (d));
    return ((unsigned long long)a) | (((unsigned long long)d) << 32);;
}

int main(int argc, char *argv[]) {
    // random vars to simulate real conditions
    int execution_time = 0;
    int return_status = 0;

    int return_status_temp = 0;

    // init rand with the number of cpu clocks
    unsigned long long int clock_ticks = 0;
    clock_ticks = rdtsc();
    srand((unsigned int)clock_ticks);

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
