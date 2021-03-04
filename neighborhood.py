import operator
from collections import deque
from copy import deepcopy
from random import randint
from time import time

from data import Data
from orders import Order
from solution import Solution


def scanNeighborhood(solution, best):
    start_time = time()
    
    sequencing, hasBetter = get_sequencing_neighbor(solution, best)
    if hasBetter:
        print('Found a better solution.')
        return sequencing, True
    
    assignment, hasBetter = get_assignment_neighbor(solution, best)
    if hasBetter:
        print('Found a better solution.')
        return assignment, True    
    sequencing += assignment
    
    finalNeighborhood =  sorted(sequencing, key= lambda x: (x.tardiness,x.makespan))
    
    print('Neighborhood size: ', len(finalNeighborhood), ' ', time()-start_time, ' seconds')
    return finalNeighborhood, False

def get_assignment_neighbor(solution, best):
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
      
                if len(assignmentNeighbors) > 75:
                    return assignmentNeighbors, False
      
                if neighbor.isBetter(best):
                    return neighbor, True
    
    return assignmentNeighbors, False

def get_sequencing_neighbor(solution, best):
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
        
            if len(sequencingNeighbors) > 75:
                return sequencingNeighbors, False 
            
            if neighbor.isBetter(best):
                return neighbor, True
    
    return sequencingNeighbors, False
