import pandas as pd

from data import Data

Data.initialize('setups.csv','orders4.csv','processing.csv','stock.csv')

class Order:
    def __init__(self, orderNumber):
        self.id = orderNumber
        
        self.productId = Data.orders.iloc[self.id]['product'] - 1
        self.quantity = Data.orders.iloc[self.id]['quantity']
        self.due = Data.orders.iloc[self.id]['due'] 

        processingTimesFiltered= Data.proctimes[self.productId][~Data.proctimes[self.productId].isnull()]
        processingTimesSorted = processingTimesFiltered.sort_values()
        self.machines = [machine for machine in processingTimesSorted.index]
        
        self.durationList = [self.quantity*Data.proctimes.iloc[machine][self.productId] for machine in self.machines]


        # previousDuration = 0
        # first = True
        # indcsToDel = []
        # for i in range(len(self.durationList)):
        #     duration = self.durationList[i]
        #     if not first:
        #         if duration > 4*previousDuration:
        #             del self.machines[i]
        #             indcsToDel.append(i)
        #     previousDuration = duration
        #     first = False
        
        # for i in indcsToDel:
        #     del self.durationList[i]
        
        durationDataFrame = pd.DataFrame(self.durationList)
        self.duration = pd.DataFrame.transpose(durationDataFrame)
        self.fastestPossible = min(self.durationList)
        self.duration.columns = [str(i) for i in self.machines]

    @staticmethod
    def populateOrders():
        Order.Orders = [Order(i) for i in range(len(Data.orders.index))]
        Order.OrdersSorted = sorted(Order.Orders, key=lambda x: (x.due, -x.fastestPossible))
        Order.OrderIds = [order.id for order in Order.OrdersSorted]
        Order.Dict = {i: Order.Orders[i] for i in [order.id for order in Order.Orders]}
        print('\n Order durations: ')
        for order in Order.OrdersSorted:
            print(order.due, order.durationList)   

