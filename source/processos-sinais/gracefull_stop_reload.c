#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <libconfig.h>

#define CONFIG_FILE "gracefull_stop_reload.cfg"

int main(int argc, char *argv[]) {
    FILE *f = NULL;
    config_t config = NULL;
    char *add_string = NULL;
    int counter = 0;

    // init and read config
    config_init(&config);
    if(config_read_file(&config, CONFIG_FILE) == CONFIG_FALSE) {
        printf("Error while reading config file\n");
        config_destroy(&config);
        exit(EXIT_FAILURE);
    }
    // read 'add_string'
    config_lookup_string(&config, "add_string", (const char**)(&add_string));
    // print 'counter + add_string' every second 
    counter = 1;
    while (1) {
        printf("%d %s\n", counter, add_string);
        counter++;
        sleep(1);
    }
    // cleanup
    config_destroy(&config);  
    return 0;
}
