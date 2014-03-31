#!/usr/bin/env python

import random # See: http://docs.python.org/2/library/random.html
import time
import sys

MIN_EXECUTION_TIME = 1
MAX_EXECUTION_TIME = 4
PROBABILITY = 1.0 / 4.0
SUCCESS = 0
FAILURE = 1

def run():
    
    # There is no need to init seed, because "current system time is used"
    # And "If randomness sources are provided by the operating system, they 
    # are used instead of the system time"
    # See: http://docs.python.org/2/library/random.html#random.seed
    
    # Generate execution time: MIN_EXECUTION_TIME <= execution_time <= MAX_EXECUTION_TIME
    execution_time = random.randint(MIN_EXECUTION_TIME, MAX_EXECUTION_TIME)
    # Generate return status: random[0,1) < PROBABILITY => FAILURE
    if random.random() < PROBABILITY:
        return_status = FAILURE
    else:
        return_status = SUCCESS
    # Simulate the program execution time
    time.sleep(execution_time)
    # Simulate a program which sometimes fail
    sys.exit(return_status)
 
# Called from command line
# See: http://stackoverflow.com/a/419986/2530295
if __name__ == "__main__":
    run()
