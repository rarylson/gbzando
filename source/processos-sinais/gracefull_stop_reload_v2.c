#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <libconfig.h>

#define CONFIG_FILE "gracefull_stop_reload.cfg"
#define STATE_FILE "gracefull_stop_reload.state"

// global vars
static config_t config;
static char *add_string;
static int counter;

// get the last value of counter
int init_counter() {
    FILE *f;
    int counter;

    if(!(f = fopen(STATE_FILE, "r"))) { // if there isn't file, return 1 
        counter = 1;
    } else { // else, return last count
        fscanf(f, "%d", &counter);
    }
    return counter;
}

// persist counter in the STATE_FILE
void persist_counter(int counter) {
    FILE *f;

    if(!(f = fopen(STATE_FILE, "w"))) {
        // error
        printf("Error while openning state file\n");
        exit(EXIT_FAILURE);
    }
    // insert 'counter' and close file
    fprintf(f, "%d", counter);
    fclose(f);
}

// read configuration and get 'add_string'
void read_config(config_t *config, const char **add_string) {
    // read config
    if(config_read_file(config, CONFIG_FILE) == CONFIG_FALSE) {
        printf("Error while reading config file\n");
        config_destroy(config);
        exit(EXIT_FAILURE);
    }
    // read 'add_string'
    config_lookup_string(config, "add_string", add_string);
}

// handler. shut down gracefully
static void stop_handler(int signal) {
    // persist counter
    persist_counter(counter);
    // now, we can shutdown safelly
    exit(EXIT_SUCCESS);
}

// handler. reload config file
static void reload_handler(int signal) {
    read_config(&config, (const char **)(&add_string));
}

int main(int argc, char *argv[]) {
    // set handlers
    // SIGINT and SIGTERM: gracefull stop
    if ((signal(SIGINT, stop_handler) == SIG_ERR) ||
            (signal(SIGTERM, stop_handler) == SIG_ERR)) {
        printf("Error while setting a signal handler\n");
        exit(EXIT_FAILURE);
    }
    // SIGHUP: reload
    if (signal(SIGHUP, reload_handler) == SIG_ERR) {
        printf("Error while setting a signal handler\n");
        exit(EXIT_FAILURE);
    }
    // init and read config
    config_init(&config);
    read_config(&config, (const char **)(&add_string));
    // print 'counter + add_string' every second 
    counter = init_counter(); // get last counter
    while (1) {
        printf("%d %s\n", counter, add_string);
        counter++;
        sleep(1);
    }
    // cleanup
    config_destroy(&config);
    return 0;
}
