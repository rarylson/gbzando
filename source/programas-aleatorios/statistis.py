#!/usr/bin/env python

import subprocess
import time

CHILD_COMMAND = "/usr/bin/env python maybe_it_works.py"
NUMBER_OF_TESTS = 500

def statistics():
    # Arrays with execution history
    time_history = []
    return_history = []

    # Collect statistics
    for i in range(0, NUMBER_OF_TESTS):
        start_time = time.time()
        return_code = subprocess.call(CHILD_COMMAND.split(" "))
        execution_time = time.time() - start_time
        # Update history
        # Round execution_time after update. Example: 1.03s to 1s
        time_history.append( round(execution_time) )
        return_history.append(return_code)
    # Count items, dividing by the total
    # Example: [1, 2, 2] -> {'1': 0.33, '2': 0.66}
    # See: http://stackoverflow.com/a/9604768/2530295
    counter_time = dict([(i, float(time_history.count(i)) / len(time_history)) 
            for i in set(time_history)])
    counter_return = dict([(i, float(return_history.count(i)) / len(return_history)) 
            for i in set(return_history)])
    # Print statistics
    print "Execution time:\n"
    print "Time\t\tPercent"
    for key, value in counter_time.iteritems():
        print "{}s\t\t{}%".format(key, value * 100)
    print "\nReturn code:\n"
    print "Code\t\tPercent"
    for key, value in counter_return.iteritems():
        print "{}\t\t{}%".format(key, value * 100)

if __name__ == "__main__":
    statistics()
