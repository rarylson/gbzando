#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>
#include <time.h>

#define CHILD_PATH "./improved_maybe_it_works"
#define TIME_PATH "/usr/bin/time"

int main(int argc, char *argv[]) {
    pid_t pid = 0;
    int status = 0;
    clock_t clock_tick = 0;
    char clock_tick_str[100];
    int i = 0;
    unsigned long int j = 0;

    for (i = 0; i < 10; i++) {
        // doing some hard work, trying to force time between clock()'s
        // to be greater then CLOCKS_PER_SEC
        for(j = 0; j < 123456789; j++) { for(j = 0; j < 123456789; j++) {} }
        // getting no. of processor clock ticks 
        clock_tick = clock(); 
        sprintf(clock_tick_str, "%d", (int)(clock_tick));

        pid = fork();
        if (pid >= 0) { // fork sucessful
            if (pid == 0) { // child
                // exec child program passing clock_tick as param (seed)
                execl(TIME_PATH, TIME_PATH, "--quiet", "-f", "time: %E\nexit: %x", 
                        CHILD_PATH, clock_tick_str, (char *)(NULL));
            }
        } else {
            printf("Error on fork\n");
        }
    }
    while(wait(&status) > 0) { } // waiting until all children die
    
    return 0;
}

