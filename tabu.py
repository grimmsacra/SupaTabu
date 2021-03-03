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
        
        if hasBetter:
            neighborCounter = 0
            neighborPicked = 0
            if current_solution._isSequencingNeighbor:
                sequencing_tabus.append(current_solution._tabu)
                if len(sequencing_tabus) > 10:
                    sequencing_tabus.popleft()
            else:
                assignment_tabus.append(current_solution._tabu)
                if len(assignment_tabus) > 10:
                    assignment_tabus.popleft()
            current_solution = neighborhood
            neighborPicked = neighborCounter
            if current_solution.tardiness < best_solution.tardiness: #compare to best
                best_solution = current_solution #update best
                counter = 0 #reset counter
        #  elif current_solution.tardiness == best_solution.tardiness:
            if current_solution.makespan < best_solution.makespan:
                best_solution = current_solution
                counter= 0
        else: 
            neighborCounter = 0
            neighborPicked = 0
            for solution in neighborhood: 
                neighborCounter += 1 
                if solution.isBetter(current_solution) and not solution.is_tabu(assignment_tabus, sequencing_tabus): #check better tardiness and tabu
                    if current_solution._isSequencingNeighbor:
                        sequencing_tabus.append(current_solution._tabu)
                        if len(sequencing_tabus) > 10:
                            sequencing_tabus.popleft()
                    else:
                        assignment_tabus.append(current_solution._tabu)
                        if len(assignment_tabus) > 10:
                            assignment_tabus.popleft()
                    current_solution = solution #update current solution
                    neighborPicked = neighborCounter
                    if current_solution.tardiness < best_solution.tardiness: #compare to best
                        best_solution = current_solution #update best
                        counter = 0 #reset counter
                #  elif current_solution.tardiness == best_solution.tardiness:
                    if current_solution.makespan < best_solution.makespan:
                        best_solution = current_solution
                        counter= 0
                    break

            if current_solution.makespan >= best_solution.makespan:
                counter += 1
                if counter == 5:
                    if current_solution._isSequencingNeighbor:
                        sequencing_tabus.append(current_solution._tabu)
                        if len(sequencing_tabus) > 5:
                            sequencing_tabus.popleft()
                    else:
                        assignment_tabus.append(current_solution._tabu)
                        if len(assignment_tabus) > 5:
                            assignment_tabus.popleft()
                    rand_index = randint(1, int(0.5* len(neighborhood)))
                    #current_solution= best_solution
                    current_solution = neighborhood[rand_index]
                    neighborPicked = rand_index + 1
                    counter = 0
        


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
        print('Iteration: ', i, ' Neighborhood sizes: ', len(assignment_tabus), len(sequencing_tabus))
        print('Iteration: ', i, ' Current solution: ', current_solution._solution)
        print('Iteration: ', i, ' Current solution: ', [current_solution.makespan, current_solution.tardiness])
        print('Iteration: ', i, ' Best solution: ', [best_solution.makespan, best_solution.tardiness])
        print('Iteration: ', i, ' Stuck counter: ', counter, '\n')

    return [best_solution.makespan, best_solution.tardiness, time()-start_time, i, best_solution._solution]
