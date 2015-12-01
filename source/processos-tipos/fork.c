#include <unistd.h>
#include <stdio.h>

int main(int argc, char *argv[]) {
    pid_t pid = 0;

    pid = fork();
    if (pid >= 0) { // fork successful
        if (pid != 0) { // parent
            printf("Parent process... Infinite loop\n");
        } else { // child
            printf("Child process... Infinite loop\n");
        }
        // infinite loop
        while (1) {
            sleep(5); // sleeping (low cpu usage)
        }   
    }
    return 0;
}
