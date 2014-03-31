#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>

#define PAUSE_BETWEEN_LAUNCHES 1
#define CHILD_PATH "./maybe_it_works"

int main(int argc, char *argv[]) {
    pid_t pid = 0;
    int status = 0;
    int errors = 0; // children that finished with errors
    int total = 0; // total of children that finished
    float percent = 0;

    while (1) { // indefinidely fork and exec children
        sleep(PAUSE_BETWEEN_LAUNCHES);
        pid = fork();
        if (pid >= 0) { // fork successful
            if (pid != 0) { // parent
                wait(&status); // wait until child die
                // update counters
                if (WIFEXITED(status) && WEXITSTATUS(status) != EXIT_SUCCESS) {
                    errors++;
                }   
                total++;
                // print statistics
                percent = (float)(errors) / total * 100;
                printf("Errors: %d, Total: %d, Percent: %.2f%%\n", errors, total, 
                        percent);
            } else { // child
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
