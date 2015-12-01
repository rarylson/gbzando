#include <unistd.h>
#include <stdio.h>
#include <sys/file.h>

int main(int argc, char *argv[]) {
    pid_t pid = 0;
    const char* FILENAME = "waiting_file.txt";
    FILE *f = NULL; // file descriptor

    pid = fork();
    if (pid >= 0) { // fork successful
        if (pid != 0) { // parent
            f = fopen(FILENAME, "w");
            // See: http://stackoverflow.com/a/7573369
            flock(fileno(f), LOCK_EX); // locking the file
            while (1) { } // infinite loop
        } else { // child
            sleep(2); // forcing parent to execute before
            f = fopen(FILENAME, "w");
            flock(fileno(f), LOCK_EX); // waiting for I/O - deadlock here
            while (1) { } // infinite loop - only will execute if parent dead            
        }
    }
    fclose(f); // never executed
    return 0;
}
