import operator
from collections import deque
from copy import deepcopy
from random import randint
from time import time

from data import Data
from neighborhood import scanNeighborhood
from orders import Order
from solution import Solution


def TabuSearch(initial_solution):
    print('\n\nStarting Tabu with solution: ', initial_solution._solution)
    print('Starting Tabu with solution: ', [initial_solution.makespan, initial_solution.tardiness])
    print('\n')
    global current_solution 
    current_solution = initial_solution
    global best_solution 
    best_solution = initial_solution
    global assignment_tabus
    assignment_tabus = deque()
    global sequencing_tabus
    sequencing_tabus = deque()

    max_iterations = 150
    global stuckCounter 
    stuckCounter = 0
    global updated
    updated = False
    counter = 0
    start_time = time()
    tardiness_reset_counter = 0
    for i in range(max_iterations):
        print('\n Iteration: ', i, '------------------------------------------')
        neighborhood, hasBetter = scanNeighborhood(current_solution)
        
        for solution in neighborhood:
            if solution.isBetter(current_solution) and not solution.is_tabu(assignment_tabus, sequencing_tabus): #check better tardiness and tabu
                if current_solution._isSequencingNeighbor:
                    sequencing_tabus.append(current_solution._tabu)
                    if len(sequencing_tabus) > 5:
                        sequencing_tabus.popleft()
                else:
                    assignment_tabus.append(current_solution._tabu)
                    if len(assignment_tabus) > 5:
                        assignment_tabus.popleft()
                current_solution = solution #update current solution
                
                if current_solution.tardiness < best_solution.tardiness: #compare to best
                    best_solution = current_solution #update best
                    counter = 0 #reset counter
                elif current_solution.tardiness == best_solution.tardiness:
                    if current_solution.makespan < best_solution.makespan:
                        best_solution = current_solution
                        counter= 0
                break

        if current_solution.makespan >= best_solution.makespan:
            counter += 1
            if counter == 5:
                if tardiness_reset_counter == 5:
                    current_solution = best_solution
                    counter = 0
                    tardiness_reset_counter = 0
                else: 
                    if current_solution._isSequencingNeighbor:
                        sequencing_tabus.append(current_solution._tabu)
                        if len(sequencing_tabus) > 5:
                            sequencing_tabus.popleft()
                    else:
                        assignment_tabus.append(current_solution._tabu)
                        if len(assignment_tabus) > 5:
                            assignment_tabus.popleft()
                    #tabus.append(current_solution)
                    
                    rand_index = randint(1, int(0.5* len(neighborhood)))
                    current_solution = neighborhood[rand_index]
                    counter = 0
        
        # if hasBetter:
        #     current_solution = current_solution.updateSolution(neighborhood, assignment_tabus, sequencing_tabus, stuckCounter)
        # else: 
        #     current_solution = neighborhood[randint(int(len(neighborhood)/2),len(neighborhood))]
        #     # current_solution = current_solution.updateFromNeighborhood(neighborhood, assignment_tabus, sequencing_tabus, stuckCounter)

        # if current_solution.isBetter(best_solution):
        #     best_solution = current_solution
        #     stuckCounter = 0
        # else:
        #     stuckCounter += 1
        
        # if stuckCounter == 15:
        #     current_solution = best_solution
        #     assignment_tabus.clear()
        #     sequencing_tabus.clear()
        #     stuckCounter = 0

        print('Iteration: ', i, '----------------------', time()-start_time,'--------------------')
        print('Iteration: ', i, ' Current solution: ', current_solution._solution)
        print('Iteration: ', i, ' Current solution: ', [current_solution.makespan, current_solution.tardiness])
        print('Iteration: ', i, ' Best solution: ', [best_solution.makespan, best_solution.tardiness])
        print('Iteration: ', i, ' Stuck counter: ', counter, '\n')

    return [best_solution.makespan, best_solution.tardiness, time()-start_time, i, best_solution._solution]
