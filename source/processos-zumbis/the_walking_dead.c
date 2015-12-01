#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#define SLEEP_TIME 5

int main(int argc, char *argv[]) {
    pid_t pid;

    while (1) { // indefinidely fork
        sleep(SLEEP_TIME); // creating childrens SLEEP_TIME to SLEEP_TIME seconds
        pid = fork();
        if (pid >= 0) { // fork successful
            if (pid == 0) { // child - print and exit
                printf("Child created and ending... Bye!\n");
                exit(EXIT_SUCCESS);
            }
        } else { // error
            printf("Error while forking\n");
        }
    }
    return 0;
}
