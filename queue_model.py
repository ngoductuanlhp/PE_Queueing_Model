#!/usr/bin/env python3
from kneed import KneeLocator 
import simpy
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import collections
from scipy.signal import argrelextrema
import time


'''PARAMETERS'''
MAX_SIMULATE_TIME = 100000 # Maximum running time
LAMBDA = 2.0000000 # mean arrival time
MU = 2.000001 # mean service rate of server
POPULATION = 100000000 # Total jobs available to generate = infinity
BUFFER = 100000000 # Maximum number of jobs the server can store in its queue length
REPLICATION = 5 # Number of replications
ALPHA = 0.1 # 
RANDOM_SEED = 4321 #Seed for random() function

'''
#####################################################################################################
---------------------------------------THEORETICAL CALCULATION---------------------------------------
#####################################################################################################
'''


'''
#####################################################################################################
-------------------------------------------SIMULATION TOOL-------------------------------------------
#####################################################################################################
'''
class Job:
    def __init__(self, name, arrival_time, serve_time):
        self.name = name
        self.arrival_time = arrival_time #time it arrives
        self.serve_time = serve_time #time intervel for serve
        self.served = 0
        self.waiting_time = 0;

class JobGenerator:
    '''
    Args:
        env:                simpy.Environment(): Environment of Simpy
        server:             Server to serve incoming jobs
        rep:                current replication
        mean_arrival_time:  parameter of exponential distribution (mean)
        mean_sevice_time:   parameter of exponential distribution (mean)
    '''

    '''
    Functions:
        Generate jobs with random arrival time and served time
    '''
    def __init__(self, env, server, rep, mean_arrival_time = 1/LAMBDA, mean_sevice_time = 1/MU):
        self.rep = rep
        self.server = server
        self.env = env
        self.mean_arrival_time = mean_arrival_time
        self.mean_sevice_time = mean_sevice_time
        self.generated_jobs_num = 0
        #Start generate jobs
        env.process(self.generateJobs(self.env))

    def generateJobs(self, env):
        while True:
            new_job_arrival_time = np.random.exponential(self.mean_arrival_time)
            new_job_service_time = np.random.exponential(self.mean_sevice_time)

            yield env.timeout(new_job_arrival_time)

            replications.job_generated[self.rep] += 1
            replications.arrival_time_list[self.rep].append(self.env.now)
            job_name = "Job" +str(self.generated_jobs_num)
            new_job = Job(job_name, replications.arrival_time_list[self.rep][-1], new_job_service_time)

            #Add new job to the list of customer of server
            self.server.job_list.append(new_job)
            self.server.queue_length+= 1

            #Check whether the server is in idle state
            if not self.server.server_idle.triggered:
                self.server.server_idle.interrupt()

class Server:
    '''
    Args:
        env:    simpy.Environment(): Environment of Simpy
        rep:    current replication
    '''

    '''
    Functions:
        Serve jobs comming from GeneratorJob
    '''
    def __init__(self, env, rep):
        self.rep = rep
        self.env = env
        self.job_list = list()

        self.queue_length = 0

        self.served_jobs_num = 0
        self.server_idle = None

        self.idle_time = 0

        #Start server
        self.env.process(self.serve())

    def serve(self):
        while True:
            #If no job to serve, server changes to ilde state
            if len(self.job_list) == 0:
                self.server_idle = self.env.process(self.sleeping())
                replications.idle_time_beginning_list[self.rep].append(self.env.now)
                #t = self.env.now
                yield self.server_idle
                replications.idle_time_duration_list[self.rep].append(self.env.now - replications.idle_time_beginning_list[i][-1])
                #self.idle_time += self.env.now - t
            else:
                #Last come first serve
                serve_job = self.job_list.pop(-1)
                self.queue_length-= 1
                
                yield self.env.timeout(serve_job.serve_time)
                serve_job.waiting_time = self.env.now - serve_job.arrival_time
                #self.waiting_time_list.append(serve_job.waiting_time);
                replications.waiting_time_list[self.rep].append(serve_job.waiting_time)
                #replications.total_waiting_time[self.rep] += serve_job.waiting_time
                #self.total_waiting_time += serve_job.waiting_time
                replications.job_served[self.rep] += 1 

    def sleeping(self):
        try:
            yield self.env.timeout(MAX_SIMULATE_TIME)
        except simpy.Interrupt:
            i = 1

class Monitor:
    '''
    Args:
        env:                simpy.Environment(): Environment of Simpy
        server:             Server to serve incoming jobs
        rep:                current replication
    '''

    '''
    Functions:
        Monitor the simulation, get queue length of the server after 1 unit of time
    '''
    def __init__(self, env, server, rep):
        self.rep = rep
        self.queue_lengths = []
        self.env = env
        self.server = server;
        self.env.process(self.monitor())

    def monitor(self):
        while True:
            replications.queue_lengths_list[self.rep].append(self.server.queue_length)
            yield self.env.timeout(1)
'''
#####################################################################################################
'''


'''Get time when start the simulation'''
start_time = time.time()



'''
#####################################################################################################
---------------CREATE GLOBAL VARIABLE TO STORE DATA OF ALL REPLICATIONS IN SIMULATION----------------
#####################################################################################################
'''
Replications = collections.namedtuple('Replication', ['job_generated', 'job_served', 'arrival_time_list', 'waiting_time_list', 
'total_waiting_time', 'average_waiting_time', 'idle_time_beginning_list', 'idle_time_duration_list', 'util', 'queue_lengths_list' ])

REPLICATIONS = [i for i in range(REPLICATION)]

job_generated_list = {rep: 0 for rep in REPLICATIONS}
job_served_list = {rep: 0 for rep in REPLICATIONS}
arrival_time_list_list = {rep: list() for rep in REPLICATIONS}
waiting_time_list_list = {rep: list() for rep in REPLICATIONS}
total_waiting_time_list = {rep: 0 for rep in REPLICATIONS}
average_waiting_time_list = {rep: 0 for rep in REPLICATIONS}

idle_time_beginning_list_list = {rep: list() for rep in REPLICATIONS}
idle_time_duration_list_list = {rep: list() for rep in REPLICATIONS}

util_list = {rep: 0 for rep in REPLICATIONS}
queue_lengths_list_list = {rep: list() for rep in REPLICATIONS}
#queue_lengths_list_list = {rep: {'Time': [], 'Length': []} for rep in REPLICATIONS}

replications = Replications(job_generated_list, job_served_list, arrival_time_list_list, waiting_time_list_list, total_waiting_time_list,
 average_waiting_time_list, idle_time_beginning_list_list, idle_time_duration_list_list, util_list, queue_lengths_list_list )
'''
#####################################################################################################
'''


'''
#####################################################################################################
-----------------------------------------RUN THE SIMULATION------------------------------------------
#####################################################################################################
'''
for i in range(REPLICATION):
    print("Turn %d" % (i + 1))
    np.random.seed(RANDOM_SEED + i)

    env = simpy.Environment()
    myServer = Server(env, i)
    myJobGenerator = JobGenerator(env, myServer, i)
    myMonitor = Monitor(env, myServer, i)

    #Start simulating
    env.run(until = MAX_SIMULATE_TIME + 1)
    #End simulating


    replications.total_waiting_time[i] = np.sum(replications.waiting_time_list[i])
    replications.average_waiting_time[i] = replications.total_waiting_time[i] / replications.job_served[i]
'''
#####################################################################################################
'''


'''
#####################################################################################################
------------------------------------------RAW DATA ANALYSIS------------------------------------------
#####################################################################################################
'''
print('Raw data analysis:')
print("Simulation time:         %d" % MAX_SIMULATE_TIME)
for i in range(REPLICATION):
    print("Turn %d" % (i + 1))
    temp = 0
    for duration in replications.idle_time_duration_list[i]:
        temp += duration
    replications.util[i] = (1.0 - temp / MAX_SIMULATE_TIME)
    print("\tNumber of job generated:     %d" % replications.job_generated[i])
    print("\tNumber of job served:        %d" % replications.job_served[i])
    print("\tTotal waiting time:          %d" % replications.total_waiting_time[i])
    print("\tAverage waiting time:        %.4f" % (replications.total_waiting_time[i] / replications.job_served[i]))
    print("\tUtilization:                 %.4f" % replications.util[i])
    print("-----------------------------------------------------------")
'''
#####################################################################################################
'''


'''
#####################################################################################################
----------------------------------VISUALIZE DATA OF ALL REPLICATION----------------------------------
#####################################################################################################
'''
for i in range(REPLICATION):
    plt.plot(replications.queue_lengths_list[i])
    plt.subplot(2, 2, 1)
    plt.title("Individual replications")

plt.subplot(2, 2, 2)
plt.title("Mean across replication")
plt.xlabel("Time")
plt.ylabel("Queue length")
average_queue_lengths = np.zeros(MAX_SIMULATE_TIME + 1)
for i in range(REPLICATION):
    average_queue_lengths = np.add(average_queue_lengths, replications.queue_lengths_list[i])
average_queue_lengths = average_queue_lengths / 4
plt.plot(average_queue_lengths)

average_q = np.sum(average_queue_lengths) / (MAX_SIMULATE_TIME + 1)
print("Average queue length of all repplication:%.2f" % average_q)

r = np.zeros(MAX_SIMULATE_TIME)
#r[i] = np.sum(q[i:]) / (MAX_SIMULATE_TIME + 1 - i) for i in range(0, MAX_SIMULATE_TIME)
for i in range(0, MAX_SIMULATE_TIME):
    r[i] = np.sum(average_queue_lengths[i:]) / (MAX_SIMULATE_TIME + 1 - i)
plt.subplot(2, 2, 3)
plt.title("Mean of last n-l replications")
plt.xlabel("Time")
plt.ylabel("Queue length")
plt.plot(r)
'''
#####################################################################################################
'''

'''
#####################################################################################################
-------------------------------TRANSIENT REMOVAL BY INIT DATA DELETION-------------------------------
#####################################################################################################
'''
# Calculate the relative change
relative_change = np.zeros(MAX_SIMULATE_TIME)
for i in range(0, MAX_SIMULATE_TIME):
    relative_change[i] = (r[i] - average_q) / average_q

#Get "knee" point: we can consider as local maxima-----------------------------------------------------------
range_simulation = range(0, MAX_SIMULATE_TIME)
local_max = KneeLocator(range_simulation, relative_change, curve = 'concave', direction = 'increasing').knee

initial_removal_time = local_max
print("Knee point: %d" % initial_removal_time)
#Init data deletion------------------------------------------------------------------------------------------
plt.subplot(2, 2, 4)
plt.title("Relative change")
plt.xlabel("Time")
plt.ylabel("Proportion")
plt.plot(relative_change)
plt.annotate('local maxima', xy=(initial_removal_time, relative_change[initial_removal_time]),
xytext=(initial_removal_time, relative_change[initial_removal_time] + 0.1), arrowprops=
dict(facecolor='red', shrink=0.03),)
'''
#####################################################################################################
'''


'''
#####################################################################################################
--------------------------TERMINATING REPLICATION BY INDEPENDENT REPLICATION-------------------------
#####################################################################################################
'''
N0 = initial_removal_time
average_ql = np.zeros(REPLICATION)

print("After transient removal:")
for i in range(REPLICATION):
    print("\tTurn %d" % (i + 1))
    idx = 0
    while idx < len(replications.arrival_time_list[i]):
        if replications.arrival_time_list[i][idx] > initial_removal_time:
            break
        else:
            idx += 1

    average_ql[i] = np.sum(replications.queue_lengths_list[i][N0:]) / (MAX_SIMULATE_TIME + 1 - N0)
    print("\tAverage length queue:              %f" % average_ql[i])

    total_waiting_time = np.sum(replications.waiting_time_list[i][idx:])
    total_job_served = replications.job_served[i] - (idx + 1)
    average_waiting_time = total_waiting_time / total_job_served

    idx = 0
    while idx < len(replications.idle_time_beginning_list[i]):
        if replications.idle_time_beginning_list[i][idx] > initial_removal_time:
            break
        else:
            idx += 1
    total_idle_time = np.sum(replications.idle_time_duration_list[i][idx:])

    print("\tNumber of job served:              %d" % total_job_served)
    print("\tTotal waiting time:                %d" % total_waiting_time)
    print("\tAverage waiting time:              %.4f" % (average_waiting_time))
    print("\tUtilization:                       %.4f" % (1 - total_idle_time / (MAX_SIMULATE_TIME - initial_removal_time)))
    print("-----------------------------------------------------------")
'''
#####################################################################################################
'''


'''
#####################################################################################################
--------------------------TERMINATING REPLICATION BY INDEPENDENT REPLICATION-------------------------
#####################################################################################################
'''
interval = np.zeros(2)
overall_mean_reps = 0
variance = 0
Z = 0
overall_mean_reps = np.sum(average_ql) / REPLICATION


for i in range(REPLICATION):
   variance += pow(average_ql[i] - overall_mean_reps , 2)
variance = variance / (REPLICATION - 1)
Z = norm.ppf(1 - ALPHA/2)
interval[0] = overall_mean_reps - Z * np.sqrt(variance)
interval[1] = overall_mean_reps + Z * np.sqrt(variance)
print("FINAL CONDITIONS")
print("\tOverall mean replications:             %f " %overall_mean_reps)
print("\tVariance:                              %f" %variance)
print("\tConfidence Interval                    (%.4f : %.4f)" % (interval[0], interval[1]))
'''
#####################################################################################################
'''

exe = time.time()-start_time
print("Total executed time                      %.4f" % exe)
print("Finish")

plt.show()