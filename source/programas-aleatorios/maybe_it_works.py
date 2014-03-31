#!/usr/bin/env python

import random
import time
import sys

MIN_EXECUTION_TIME = 1 
MAX_EXECUTION_TIME = 4 
PROBABILITY = 1.0 / 4.0 
SUCCESS = 0 
FAILURE = 1

def run():
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

if __name__ == "__main__":
    run()
