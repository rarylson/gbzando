#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

// handler for common signals that terminate process
static void end_handler(int signal) {
    printf("I will survive, baby!\n");
}

int main(int argc, char *argv[]) {
    // set handlers
    if ((signal(SIGINT, end_handler) == SIG_ERR) || (signal(SIGHUP, end_handler) ==  
            SIG_ERR) || (signal(SIGTERM, end_handler) == SIG_ERR)) {
        printf("Error while setting a signal handler\n");
        exit(EXIT_FAILURE);
    }   
    while (1) { } // infinite loop
    return 0;  
}
