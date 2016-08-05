#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <stdio.h>

// create a pidfile
// return a negative value if the file already exists
int create_pidfile(char *pidfile) {
    int fd = 0;
    FILE *f = NULL;

    // atomically create the pidfile
    fd = open(pidfile, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (fd < 0) {
        if (errno == EEXIST) {
            return -1; // file already exists
        } else {
            exit(1); // error
        }
    }
    // associate a stream with the existing file descriptor
    f = fdopen(fd, "w");
    if (!f) {
        exit(1); // error
    }
    // write the PID in the pidfile
    fprintf(f, "%ld\n", (long)(getpid()));
    fclose(f);

    return 0;
}

// remove the pidfile
void remove_pidfile(char *pidfile) {
    unlink(pidfile);
}
