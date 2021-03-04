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
    previousSolution = current_solution
    max_iterations = 500
    global stuckCounter 
    stuckCounter = 0
    global updated
    counter = 0
    counterForBest = 0
    start_time = time()
    
    for i in range(max_iterations):
        print('\n Iteration: ', i, '------------------------------------------')
        neighborhood, hasBetter = scanNeighborhood(current_solution, best_solution)
        previousSolution = current_solution
        updated = False
        tabuImprovers = []

        if hasBetter:
            if neighborhood.is_tabu:
                tabuImprovers.append(neighborhood)
            else:
                updated = True
                neighborCounter = 0
                neighborPicked = 0
                if current_solution._isSequencingNeighbor:
                    sequencing_tabus.append(current_solution._tabu)
                    if len(sequencing_tabus) > 0:
                        sequencing_tabus.popleft()
                else:
                    assignment_tabus.append(current_solution._tabu)
                    if len(assignment_tabus) > 5:
                        assignment_tabus.popleft()
                current_solution = neighborhood
                neighborPicked = neighborCounter
        else: 
            neighborCounter = 0
            neighborPicked = 0
            tabuImprovers = []
            for solution in neighborhood: 
                neighborCounter += 1 
                if solution.isBetter(best_solution) and not solution.is_tabu(assignment_tabus, sequencing_tabus):
                    tabuImprovers.append(solution)
                    
                if solution.isBetter(current_solution): #update if better and not tabu
                    if current_solution._isSequencingNeighbor:
                        sequencing_tabus.append(current_solution._tabu)
                        if len(sequencing_tabus) > 5:
                            sequencing_tabus.popleft()
                    else:
                        assignment_tabus.append(current_solution._tabu)
                        if len(assignment_tabus) > 5:
                            assignment_tabus.popleft()
                            
                    current_solution = solution #update current solution
                    neighborPicked = neighborCounter
                    updated = True
                    break
                
        if not updated and len(tabuImprovers) > 0:#updating because tabu is better
            updated = True
            current_solution = tabuImprovers[0]

        if not updated: #slingshot
            if current_solution._isSequencingNeighbor:
                sequencing_tabus.append(current_solution._tabu)
                if len(sequencing_tabus) > 5:
                    sequencing_tabus.popleft()
            else:
                assignment_tabus.append(current_solution._tabu)
                if len(assignment_tabus) > 5:
                    assignment_tabus.popleft()
            rand_index = randint(int(0.1*len(neighborhood)), int(0.5* len(neighborhood)))
                    #current_solution= best_solution
            current_solution = neighborhood[rand_index]
            neighborPicked = rand_index + 1
            counter = 0
            print('-----------Slingshot! ')
                            
        if current_solution.isBetter(best_solution):
            best_solution = current_solution
            counterForBest = 0
        else:
                counterForBest += 1
                if counterForBest == 5:
                    current_solution = best_solution
                    # assignment_tabus.clear()
                    # sequencing_tabus.clear()        
                    counterForBest = 0

        print('Iteration: ', i, '----------------------', time()-start_time,'--------------------')
        print('Iteration: ', i, ' Tabu List sizes: ', len(assignment_tabus), len(sequencing_tabus))
     #   print('Iteration: ', i, ' Current solution: ', current_solution._solution)
        print('Iteration: ', i, ' Current solution: ', [current_solution.makespan, current_solution.tardiness])
        print('Iteration: ', i, ' Best solution: ', [best_solution.makespan, best_solution.tardiness])
        print('Iteration: ', i, ' No new best counter: ', counterForBest, '\n')

    return [best_solution.makespan, best_solution.tardiness, time()-start_time, i, best_solution._solution]
