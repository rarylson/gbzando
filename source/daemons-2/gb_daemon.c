#include <signal.h>
#include <stdlib.h>
#include <syslog.h>
#include "daemon.h"
#include "daemon_pid.h"

#define PIDFILE "/run/gb_daemon.pid"
#define SLEEP_TIME 10

static void end_handler(int signal) {
    remove_pidfile(PIDFILE);
    syslog(LOG_NOTICE, "Program stopped");
    exit(0);
}

int main(int argc, char *argv[]) {
    // turn itself in a daemon and create the pidfile
    daemonize();
    if (create_pidfile(PIDFILE) < 0) {
        syslog(LOG_CRIT, "Pidfile %s already exists", PIDFILE);
        exit(1);
    }
    syslog(LOG_NOTICE, "Program started");
    // set end handler
    if (signal(SIGTERM, end_handler) == SIG_ERR) {
        exit(1); // error
    }
    // main loop
    while (1) {
        syslog(LOG_INFO, "Going to sleep %d seconds...", SLEEP_TIME);
        sleep(SLEEP_TIME);
        syslog(LOG_INFO, "Woke up!");
    }

    return 0;
}

