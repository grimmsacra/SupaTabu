from csv import writer

import numpy as np
import pandas as pd

import neighborhood
from data import Data
from orders import Order
from solution import Solution
from tabu import TabuSearch

Data.initialize('setups.csv','orders4.csv','processing.csv','stock.csv')
Order.populateOrders()
test = Solution({0: [], 1: [10, 13, 24, 0, 3, 5, 16, 19, 18, 15, 23], 2: [11, 12, 9, 1, 7, 4], 3: [2, 8, 6], 4: [20, 17, 21], 5: [29, 37, 27, 28, 36], 6: [38, 39, 34, 35, 30], 7: [32, 22, 26, 25, 31]})
test2 = Solution( {0: [24, 16, 15], 1: [10, 13, 0, 19, 18, 23], 2: [11, 12, 9, 1, 4, 7], 3: [2, 8, 3, 6], 4: [20, 17, 5, 21], 5: [29, 37, 27, 28, 36], 6: [38, 39, 34, 35, 30], 7: [32, 22, 26, 25, 31]})
test3 = Solution( {0: [19, 24, 17, 16, 18, 15], 1: [10, 13, 21, 23], 2: [11, 12, 9, 4, 7], 3: [0, 8, 3, 2, 6], 4: [20, 1, 5], 5: [29, 37, 27, 28, 36], 6: [38, 39, 34, 35, 30], 7: [31, 32, 22, 26, 25]})
supaSolution = Solution({0: [24, 20, 21, 19, 16], 1: [10, 13, 14], 2: [4, 7, 12, 11], 3: [9, 2, 6, 8, 3, 1, 5], 4: [17, 15, 23, 18, 0], 5: [29, 28, 36, 37, 27], 6: [38, 39, 35, 30, 34], 7: [32, 31, 33, 22, 26, 25]})
supa1495 = Solution( {0: [17, 24, 20, 15], 1: [13, 10, 0, 18], 2: [7, 11, 12, 1, 5], 3: [4, 9, 2, 6, 14], 4: [19, 21, 8, 3, 23, 16], 5: [29, 28, 37, 27, 36], 6: [34, 30, 35, 39, 38], 7: [22, 32, 31, 33, 26, 25]})
#testEdd = Solution.initial_solution_EDD()
initial_solution = Solution.initial_solution()
result = TabuSearch(initial_solution)

# policy = 'MTO'
# setups = 'Symmetrical'
# instance = 'Case Study'
# filename = policy + '-'  + setups + ' - ' + instance
# print(filename)
# with open(filename, 'w',newline='') as myfile:
#     resultwriter = writer(myfile,quoting=QUOTE_ALL)
#     for i in range(50):
#         initial_solution = Solution.initial_solution()
#         row = TabuSearch(initial_solution)
#         resultwriter.writerow(row)
