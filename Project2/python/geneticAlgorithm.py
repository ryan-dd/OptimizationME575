from datetime import datetime
from datetime import timedelta
import pytz
import time
import numpy as np
import json
import pandas as pd
from fitness_all import fitnessOfPath
import random
from scipy.stats import truncnorm

def fitness(generation,sessions,travel_time,daysotw,timezones,dictionary):
    m = np.size(generation,1)
    total_time = []
    for i in range(m):
        gen_time = 0
        path = generation.astype(int)
        path = path[:,i]
        listpath = str(path.tolist())
        if listpath in dictionary:
            fitness_path = dictionary[listpath]
        else:
            fitness_path = fitnessOfPath(path,sessions,travel_time,daysotw,timezones)
            dictionary[listpath] = fitness_path
        total_time.append(fitness_path)  
    return total_time

sessionFileName = 'TempleSchedules/templeEndowmentSchedules.json'
with open(sessionFileName, 'r') as file1:
    sessions = json.load(file1)

timezonesFileName = 'TimeZones/timezones.json'
with open(timezonesFileName, 'r') as file2:
    timezones = json.load(file2)
timezones = [pytz.timezone(t) for t in timezones]

timefilename = 'BetweenTempleInfo/timeBetweenLocations.txt'
travel_time = pd.read_csv(timefilename, delimiter='\t')
travel_time = travel_time.values
travel_time = np.delete(travel_time,0,1)
daysotw = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday","Saturday","Sunday"]

# Optimization Variables
cross_percent = .2 
mutat_percent = .2 #Mutation percentage 
num_gen = 20
gen_size = 20
tourny_size = int(gen_size/3)

num_temples = len(timezones)
old_gen = np.zeros((num_temples,gen_size))
parents = np.zeros((2,))
children = np.zeros((num_temples,2))
# Generate 1st Generation (Random)
generation = np.array([52,48,36,39,62,50,23,69,68,1,34,59,25,16,5,46,21,14,3,41,49,35,24,8,47,15,33,27,18,12,65,42,29,72,66,6,20,17,71,53,40,19,45,28,58,9,44,10,31,67,4,56,26,70,7,38,63,13,61,2,51,37,55,57,22,32,43,60,54,30,64,11])
col = np.subtract(generation,1)
for i in range(gen_size):
    #col = np.random.permutation(num_temples)
    old_gen[:,i] = np.transpose(col)
initial_gen = old_gen
dictionary = {}
initial_fit = fitness(old_gen, sessions, travel_time, daysotw, timezones, dictionary)
prev_fit = np.array(initial_fit)
# Generation For Loop
for gen in range(num_gen):
    # Child Generation For loop
    old_fit = prev_fit.tolist()
    # Do a tournament
    new_gen = np.zeros((num_temples,gen_size*2))
    for i in range(int(gen_size)):
        # Two tournaments for the two parents
        for j in range(2):
            # Select Parents (By fitness) (Tournament Style) 
            tourny_participants = random.sample(list(range(gen_size)), tourny_size)
            arg = np.argmin(np.array(old_fit)[tourny_participants])
            parents[j]= np.copy(tourny_participants[arg])    
        children[:,0] = np.copy(old_gen[:,np.copy(int(parents[0]))])
        children[:,1] = np.copy(old_gen[:,np.copy(int(parents[1]))])    
        #Ordered Crossover
        crossover_values = []
        for j in range(num_temples): #Iterate through the genes of the children. 
            if np.random.rand(1) < cross_percent:
                crossover_values.append(j)
        # array of the order of the values of the first parent
        if len(crossover_values) != 0:
            child1 = children[:,0]
            child2 = children[:,1]
            indices1 = np.sort([np.where(child1==cv)[0][0] for cv in crossover_values])
            indices2 = np.sort([np.where(child2==cv)[0][0] for cv in crossover_values])
            temp1 = np.copy(child1)
            temp2 = np.copy(child2)
            child1[indices1] = np.copy(temp2[indices2])
            child2[indices2] = np.copy(temp1[indices1])
        #Mutation (Uniform)
        for chil in range(2):
            for j in range(num_temples): #Iterate through the genes of the children. 
                if np.random.rand(1) < mutat_percent:
                    # Child gene insertion
                    mutated_value = np.random.randint(0,num_temples)
                    if mutated_value == children[j,chil]:
                        continue
                    gene_loc_mutate = np.argwhere(children[:,chil]==mutated_value).flatten()[0]
                    child = children[:,chil]
                    updated_child = np.insert(child,j,mutated_value)
                    if j > gene_loc_mutate:
                        child = np.delete(updated_child,gene_loc_mutate)
                    else:
                        child = np.delete(updated_child,gene_loc_mutate+1)
                    children[:,chil] = np.copy(child)
        #Store Children into new generation
        new_gen[:,2*(i+1)-2] = np.copy(children[:,0])
        new_gen[:,2*(i+1)-1] = np.copy(children[:,1])
    #Elitism (Pick top N)
    current_gen = np.concatenate((old_gen,new_gen),axis=1); #Concatenate together for fitness function
    new_fit = fitness(new_gen, sessions, travel_time, daysotw, timezones, dictionary)
    current_gen_fit = old_fit+new_fit
    winners = np.array(current_gen_fit).argsort()[:gen_size]
    old_gen = np.copy(current_gen[:,winners])
    prev_fit = np.copy(np.array(current_gen_fit)[winners])    
    print(gen) 
    # if gen%5 == 0:
    #     I = np.argmin(current_gen_fit)
    #     print(current_gen[:,I])
    #     print(current_gen_fit[I])
final_gen = old_gen
final_fit = fitness(old_gen, sessions, travel_time, daysotw, timezones, dictionary)
I = np.argmin(final_fit)
fit_opt = final_fit[I]
xopt = final_gen[:,I]+1
print([float(x) for x in xopt])
print(fit_opt)