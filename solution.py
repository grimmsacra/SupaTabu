from copy import deepcopy
from operator import itemgetter
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
    def initial_solution_EDD():
        solution = {i: [] for i in range(0,Data.num_machines)}
        solution_ops = {i:[] for i in range(0,Data.num_machines)}
        last_op_on_machine = [0] * Data.num_machines
        current_machine_time = [0] * Data.num_machines
        
        for ordertuple in Data.orders.itertuples():
            order = ordertuple[0]
            op = ordertuple[1]
            qtd = ordertuple[2]
            due = ordertuple[3]
            proctimes = Data.proctimes[op-1]
            proctimes_no_nans = proctimes[~proctimes.isnull()]
            sorted_proctimes = proctimes_no_nans.sort_values()
            for index, t in sorted_proctimes.iteritems():
                times = qtd * t
                if not last_op_on_machine[index]:
                    setup = 0
                else: 
                    setup = Data.setups.iloc[op-1][last_op_on_machine[index]-1]
                total = times + setup
                if due < current_machine_time[index] + total:
                    continue
                else:
                    solution[index].append(order)
                    solution_ops[index].append(op)
                    current_machine_time[index] += total
                    last_op_on_machine[index] = op
                    break              
        return Solution(solution)

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
                        machineCandidates = []   
                        for i in range(len(solution[machine])+1):    
                            solutionCopy = deepcopy(solution)
                            solutionCopy[machine].insert(i,order.id)
                            singleMachineList = solutionCopy[machine]
                            tardiness, makespan = Solution.calculateSingleMachine(solutionCopy[machine], machine)
                            machineCandidates.append([tardiness,makespan, solutionCopy])
                            #print(tardiness, makespan)
                        machineCandidatesSorted = sorted(machineCandidates, key= lambda x: (x[0], x[1]))
                        candidates += machineCandidatesSorted
                    candidatesSorted = sorted(candidates, key= lambda x: (x[0], x[1]))
                    solution = candidatesSorted[0][2]
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

    def updateSolution(self, newSolution, assignment_tabus, sequencing_tabus, stuckCounter, updateCounter = True):
        if updateCounter: 
            updated = True
            stuckCounter = 0
        else:
            stuckCounter += 1
        if newSolution._isSequencingNeighbor:
            sequencing_tabus.append(newSolution._tabu)
            if len(sequencing_tabus) > 5:
                sequencing_tabus.popleft()
        else:
            assignment_tabus.append(newSolution._tabu)
            if len(assignment_tabus) > 5:
                assignment_tabus.popleft()
        return newSolution

    def updateFromNeighborhood(self, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter):
        isReturn, solution = Solution.firstScan(self, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter)
        return solution if isReturn else null

        isReturn, solution = Solution.secondScan(self, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter)
        return solution if isReturn else null
    
        isReturn, solution = Solution.thirdScan(self, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter)
        return solution if isReturn else null

        isReturn, solution = Solution.fourthScan(self, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter)
        return solution if isReturn else null

    def firstScan(currentSolution, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter):
        for solution in neighborhood:
            if solution.is_tabu(assignment_tabus, sequencing_tabus):
                break
            if solution.betterTardiness(currentSolution):
                currentSolution.updateSolution(solution, assignment_tabus, sequencing_tabus, stuckCounter)
                return True, solution
            if solution.betterMakespan(currentSolution):
                currentSolution.updateSolution(solution, assignment_tabus, sequencing_tabus, stuckCounter)
                return True, solution
        return False, currentSolution
        
    def secondScan(currentSolution, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter):
        for solution in neighborhood:
            if solution.betterTardiness(currentSolution):
                currentSolution.updateSolution(solution, assignment_tabus, sequencing_tabus, stuckCounter)
                return True, solution
            if solution.betterMakespan(currentSolution):
                scurrentSolutionelf.updateSolution(solution, assignment_tabus, sequencing_tabus, stuckCounter)
                return True, solution
        return False, currentSolution

    def thirdScan(currentSolution, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter):
        for solution in neighborhood:
            if solution.notMuchWorse(currentSolution):
                currentSolution.updateSolution(solution, assignment_tabus, sequencing_tabus, stuckCounter, False)
                return True, solution
        return False, currentSolution 
                
    def fourthScan(currentSolution, neighborhood, assignment_tabus, sequencing_tabus, stuckCounter):
        for solution in neighborhood:
            if solution.considerablyWorse(currentSolution): 
                currentSolution.updateSolution(solution, assignment_tabus, sequencing_tabus, stuckCounter, False)
                return True, solution 
        return False, currentSolution

    def isBetter(self, outra):
        if self.makespan < outra.makespan and self.tardiness <= outra.tardiness:
            return True
        if self.tardiness < outra.tardiness:
            return True
        if self.total < outra.total:
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

    def notMuchWorse(self,outra):
        if outra.tardiness > 0:
            if self.makespan <= outra.makespan + 2000:
                return True
            if self.tardiness <= outra.makespan + 2000:
                return True
        if outra.tardiness == 0:
            if self.makespan <= outra.makespan + 2000 and self.tardiness <= outra.tardiness + 500:
                return True
        return False

    def considerablyWorse(self,outra):
        if self.tardiness > 0:
            if self.makespan <= outra.makespan + 5000:
                return True
        if self.betterMakespan(outra):
            return True
        if self.tardiness <= outra.tardiness + 2000:
            return True
        return False
