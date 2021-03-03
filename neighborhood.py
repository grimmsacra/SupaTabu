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
        tardiness = solution.orderTardiness[orderId]
        setup = solution.orderSetup[orderId]
        duration = solution.orderTotal[orderId]
        
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
                assignmentNeighbors.append(neighbor)
      
                # if len(assignmentNeighbors) > 100:
                #     print('Generated Assignment Neighbors: ', len(assignmentNeighbors), '   ', time()-startTime)
                #     return assignmentNeighbors, False
      
                if neighbor.isBetter(solution):
                    # print('Found a better solution in :', time()-startTime)
                    return neighbor, True
        
    # print('Generated Assignment Neighbors: ', len(assignmentNeighbors), '   ', time()-startTime)
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
        
            # if len(sequencingNeighbors) > 100:
            #     print('Generated Sequencing neighbors, Time:  ', len(sequencingNeighbors), '  ', time()-startTime)
            #     return sequencingNeighbors, False 
            
            if neighbor.isBetter(solution):
                # print('Found a better solution in :', time()-startTime)
                return neighbor, True
    
    # print('Generated Sequencing neighbors, Time:  ', len(sequencingNeighbors), '  ', time()-startTime)
    return sequencingNeighbors, False
