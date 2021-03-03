import operator
from collections import deque
from copy import deepcopy
from random import randint
from time import time

from data import Data
from orders import Order
from solution import Solution


class Neighborhood:
    def __init__(self, originalSolution):
        self.solutions = []
        self.originalSolution = originalSolution
    
    def join(self,neighborhood):
        self.solutions += neighborhood.solutions
        return self.solutions

    def add(self, solution):
        self.solutions.append(solution)
        print(len(self.solutions))
            
    def remove(self, solution):
        self.solutions.delete(solution)

    def getNeigborBest(self):
        return self.solutions[0]

    def sortNeighborhood(self):
        if self.originalSolution.tardiness > 0: 
            self.solutions = sorted(self.solutions, key = lambda x: (x.tardiness, x.makespan))
        self.printNeighborhoodScores()

    def printNeighborhoodScores(self):
        aux = [[x.makespan, x.tardiness] for x in self.solutions]
        aux2 = [x._solution for x in self.solutions]
        print(aux[:10])
        #print(aux2[:10])

def scanNeighborhood(solution):
    start_time = time()
    
    sequencing, hasBetter = get_sequencing_neighbor(solution)
    if hasBetter:
        return sequencing, True
    
    assignment, hasBetter = get_assignment_neighbor(solution)
    if hasBetter:
        return assignment, True    
    sequencing += assignment
    
    finalNeighborhood =  sorted(sequencing, key= lambda x: (x.tardiness, x.makespan))
    
    print('Neighborhood size: ', len(finalNeighborhood), ' ', time()-start_time, ' seconds')
    return finalNeighborhood, False

def get_assignment_neighbor(solution):
    startTime = time()
        
    criticalPath = solution.criticalPath
    criticalMachine = solution.criticalMachine
    criticalPathSorted = []
    for orderId in Order.OrderIds:
        if orderId in criticalPath:
            criticalPathSorted.append(orderId)
    
    assignmentNeighbors = []
    
    for orderId in criticalPathSorted:   
        order = Order.Dict[orderId]
        assignmentNeighborsAid = []
        for machine in order.machines:
            for i in range(len(solution._solution[machine])+1): 
                neighborDict = deepcopy(solution._solution)
                neighborDict[criticalMachine].remove(orderId)
                neighborDict[machine].insert(i,orderId)
                neighbor = Solution(neighborDict)
                neighbor._isSequencingNeighbor = False
                neighbor._tabu = [orderId,criticalMachine]
                assignmentNeighborsAid.append(neighbor)
            
                # if neighbor.isBetter(solution):
                #     print('Found a better solution in :', time()-startTime)
                #     return neighbor, True

        assignmentNeighbors += assignmentNeighborsAid
        
        # if len(assignmentNeighbors) >= 25:
        #     return assignmentNeighbors, False
        
    print('Generated Assignment Neighbors: ', len(assignmentNeighbors), '   ', time()-startTime)
    return assignmentNeighbors, False

def get_sequencing_neighbor(solution):
    startTime = time()
    criticalPath = solution.criticalPath
    criticalMachine = solution.criticalMachine
    criticalPathSorted = []
    
    for orderId in Order.OrderIds:
        if orderId in criticalPath:
            criticalPathSorted.append(orderId)
    
    sequencingNeighbors = []
    for order in criticalPathSorted:
        for i in range(0,len(criticalPath)+1):
            neighborDict = deepcopy(solution._solution)
            neighborDict[criticalMachine].remove(order)
            neighborDict[criticalMachine].insert(i,order)
            
            neighbor = Solution(neighborDict)
            neighbor._tabu = [orderId,neighborDict[criticalMachine][i-1]]
            
            sequencingNeighbors.append(neighbor)
        
        # if len(sequencingNeighbors) > 25:
        #     return sequencingNeighbors, False
        
            # if neighbor.isBetter(solution):
            #     print('Found a better solution in :', time()-startTime)
            #     return neighbor, True
    print('Generated Sequencing neighbors, Time:  ', len(sequencingNeighbors), '  ', time()-startTime)
    return sequencingNeighbors, False

def TabuSearch(initial_solution):
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
