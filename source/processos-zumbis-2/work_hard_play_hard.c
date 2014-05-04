#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>

#define PAUSE_BETWEEN_LAUNCHES 2
#define CHILD_PATH "./maybe_it_works"

// process SIGCHLD signals
static void sigchld_handler(int signum) {
    static int errors = 0; // children that finished with errors
    static int total = 0; // total of children that finished
    float percent = 0;
    int status = 0;

    // loop through all died children
    while(waitpid(-1, &status, WNOHANG) > 0) {
        // update counters
        if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS) {
            errors++;
        }
        total++;
    }   
    // print statistics
    percent = (total != 0) ? (float)(errors) / total * 100 : 0;
    printf("Errors: %d, Total: %d, Percent: %.2f%%\n", errors, total, percent);
}

int main(int argc, char *argv[]) {
    pid_t pid = 0;
    int sleep_remaining = 0; // remaining time to sleep

    // set handler to SIGCHLD
    if (signal(SIGCHLD, sigchld_handler) == SIG_ERR) {
        printf("Error while setting a signal handler\n");
        exit(EXIT_FAILURE);
    }

    while (1) { // indefinidely fork and exec children
        // sleep the expected time, even if an interruption occurs
        sleep_remaining = PAUSE_BETWEEN_LAUNCHES;
        while ((sleep_remaining = sleep(sleep_remaining)) > 0) { }
        pid = fork();
        if (pid >= 0) { // fork successful
            if (pid == 0) { // child
                if (! execl(CHILD_PATH, CHILD_PATH, (char *)(NULL))) { // exec child program
                    printf("Error on exec\n");
                    exit(EXIT_FAILURE);
                }
            }
        } else {
            printf("Error on fork\n");
        }
    }

    return 0;
}
