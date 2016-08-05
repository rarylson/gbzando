#ifndef DAEMON_PID_H
#define DAEMON_PID_H
int create_pidfile(char *pidfile);
void remove_pidfile(char *pidfile);
#endif
