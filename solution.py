from copy import deepcopy
from operator import itemgetter
from random import randint
from time import time

from data import Data
from orders import Order


class Solution:
    def __init__(self,solution):
        self._solution = solution

        self.makespan = 0
        self.machineTotals = [0 for i in Data.proctimes.index]
        self.machineTardiness = [0 for i in Data.proctimes.index]
        self.total = 0
        self.tardiness = 0
        self.criticalPath = []
        self.criticalMachine = []

        self.orderTail = [0 for order in Order.Orders]
        self.orderTotal = [0 for order in Order.Orders]
        self.orderSetup = [0 for order in Order.Orders]
        self.orderTardiness = [0 for order in Order.Orders]

        self.calculateObjectiveFunctions()
        self._isSequencingNeighbor = True
        self._tabu = []

    @staticmethod
    def initial_solution():
        print('Generating Initial Solution')
        startTime = time()
        solution = {i: [] for i in range(0, Data.num_machines)}    #solution to be updated from candidates 
        ordersToGo = [i for i in range(0, Data.num_orders)]
        ordercounter = [0 for i in range(Data.num_orders)]
        while len(ordersToGo) > 0: 
            for orderId in Order.OrderIds:
                order = Order.Dict[orderId]
                print('Inserting order ',orderId, order.durationList)
                if order.id in ordersToGo:  
                    candidates = []  
                    for machine in order.machines:    
                        for i in range(len(solution[machine])+1):    
                            solutionCopy = deepcopy(solution)
                            solutionCopy[machine].insert(i,order.id)
                            
                            # singleMachineList = solutionCopy[machine]
                            # tardiness, makespan = Solution.calculateSingleMachine(solutionCopy[machine], machine)
                            solutionCopyObj = Solution(solutionCopy)                            
                            candidates.append(solutionCopyObj)
                            #print(tardiness, makespan)
                        
                    candidatesSorted = sorted(candidates, key= lambda x: (x.tardiness, x.total))
                    solution = candidatesSorted[randint(0,int(len(candidatesSorted)/8))]._solution
                    ordersToGo.remove(orderId)
        print("Initial solution time: ", time()-startTime)
        return Solution(solution)

    def calculateObjectiveFunctions(self):
        startTime = time()
        for machine in self._solution:
            first = True
            runningTotal = 0
            runningTardiness = 0

            for orderId in self._solution[machine]:
                self.orderTail[orderId] = runningTotal 
                order = Order.Dict[orderId]
                orderDuration = order.duration.iloc[0][str(machine)]

                if (first or lastOperationOnMachine == order.productId):
                    self.orderSetup[orderId]  = 0
                    first = False
                else: 
                    self.orderSetup[orderId]  = Data.setups.iloc[lastOperationOnMachine][order.productId]

                self.orderTotal[orderId] = self.orderSetup[orderId]  + orderDuration

                runningTotal += self.orderTotal[orderId]
                lastOperationOnMachine = order.productId

                if order.due < runningTotal:
                    self.orderTardiness[orderId] = runningTotal - order.due
                    runningTardiness += runningTotal - order.due
            
            self.machineTotals[machine] = runningTotal
            self.machineTardiness[machine] = runningTardiness
            
        # self.numberOfOrders = sum([len(self._solution[i]) for i in range(Data.num_machines)])
        # print('number of orders in solution: ', self.numberOfOrders)
        
        self.total = sum(self.machineTotals)
        self.tardiness = sum(self.machineTardiness)
        self.makespan = max(self.machineTotals)
        self.criticalMachine = self.machineTotals.index(max(self.machineTotals))
        self.criticalPath = self._solution[self.criticalMachine]
        # print('Solution: ', self.makespan, self.tardiness, time()-startTime)
        # print('Solution dict: ', self._solution)
        # for i in range(len(self._solution)):
        #     Solution.calculateSingleMachine(self._solution[i], i)

    def calculateSingleMachine(orders, machine):
        startTime = time()
        first = True
        runningTotal = 0
        runningTardiness = 0

        for orderId in orders:
            order = Order.Dict[orderId]
            if (first or lastOperationOnMachine == order.productId):
                setup = 0
            else: 
                setup = Data.setups.iloc[lastOperationOnMachine][order.productId]
            first = False

            orderDuration = order.duration.iloc[0][str(machine)]
            orderTotal = setup + orderDuration
            runningTotal += orderTotal

            lastOperationOnMachine = order.productId

            if Data.orders.iloc[order.id]['due']  < runningTotal:
                runningTardiness += runningTotal - order.due
       # print('calculated single machine: ', time()-startTime)
        return runningTardiness, runningTotal
        

    def is_tabu(self, assignment_tabus, sequencing_tabus):
        for pair in assignment_tabus:
            orderId = pair[0]
            tabuMachine = pair[1]
            for machine in self._solution:
                if machine == tabuMachine and orderId in self._solution[machine]:
                    return True  
        for pair in sequencing_tabus:
            if pair!= 0:   
                for key in self._solution:
                    if tuple(pair) in list(zip(self._solution[key][:1], self._solution[key][1:])):
                        return True                             
        return False

    def isBetter(self, outra):
        if self.makespan < outra.makespan and self.tardiness <= outra.tardiness:
            return True
        if self.tardiness < outra.tardiness and self.makespan <= outra.makespan:
            return True
        return False

    def betterMakespan(self, currentBest):
        if self.tardiness > currentBest.tardiness:
            return False
        if currentBest.tardiness > 0 and self.tardiness < currentBest.tardiness:
            return True
        if self.makespan <= currentBest.makespan:
            return True
        return False
    
    def betterTardiness(self, outra):
        if self.tardiness < outra.tardiness:
            return True
        return False
