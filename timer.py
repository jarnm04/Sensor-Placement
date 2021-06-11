# This is a timing script meant to produce data on exeuctions of the three implementations
# Written by: Joshua Rinaldi
# AFIT/ENG CSCE 686, Spring 2021 Final Project

import subprocess
import os
from functools import partial
import timeit
import matplotlib.pyplot as plt

import deterministic
import localSearch
import GA

def determWrapper(file):
    def wrapped():
        return deterministic.determDriver(file, 2)
    return wrapped

def GAWrapper(file):
    def wrapped():
        return GA.GADriver(file, 2)
    return wrapped

def localWrapper(file):
    def wrapped():
        return localSearch.localSearchDriver(file, 2)
    return wrapped

print("#############DETERMINISTIC EXECUTIONS##############")
print("Graph 1 Execution: ")
dtime1 = timeit.timeit(stmt = partial(determWrapper("test1.txt")), number = 1)
print("Graph 2 Exeuction: ")
dtime2= timeit.timeit(stmt = partial(determWrapper("test2.txt")), number = 1)
print("Graph 3 Exeuction: ")
dtime3 = timeit.timeit(stmt = partial(determWrapper("test3.txt")), number = 1)

print("very small graph time: {}".format(dtime1))
print("small time: {}".format(dtime2))
print("medium time: {}".format(dtime3))

print("###################################################")
print("##################GA EXECUTIONS####################")
print("Graph 1 Execution: ")
gtime1 = timeit.timeit(stmt = partial(GAWrapper("test1.txt")), number = 1)
print("Graph 2 Exeuction: ")
gtime2 = timeit.timeit(stmt = partial(GAWrapper("test2.txt")), number = 1)
print("Graph 3 Exeuction: ")
gtime3 = timeit.timeit(stmt = partial(GAWrapper("test3.txt")), number = 1)

print("very small graph time: {}".format(gtime1))
print("small time: {}".format(gtime2))
print("medium time: {}".format(gtime3))


print("###################################################")
print("##################LOCAL EXECUTIONS#################")
print("Graph 1 Execution: ")
ltime1 = timeit.timeit(stmt = partial(localWrapper("test1.txt")), number = 1)
print("Graph 2 Exeuction: ")
ltime2 = timeit.timeit(stmt = partial(localWrapper("test2.txt")), number = 1)
print("Graph 3 Exeuction: ")
ltime3 = timeit.timeit(stmt = partial(localWrapper("test3.txt")), number = 1)

print("very small graph time: {}".format(ltime1))
print("small time: {}".format(ltime2))
print("medium time: {}".format(ltime3))