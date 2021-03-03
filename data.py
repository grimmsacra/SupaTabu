from numpy import arange
from pandas import DataFrame, read_csv


class Data:
    @staticmethod
    def reset_Data():
        Data.setups = None
        Data.orders = None
        Data.usable_machines = {}
        Data.proctimes = None
        Data.ops = []
        Data.num_ops = 0
        Data.num_machines = 0
        Data.num_orders = 0

    @staticmethod
    def read_setups(ficheiro_setups):
        dfsetups = read_csv(ficheiro_setups)
        df2 = DataFrame(data=dfsetups)
        df2.columns = arange(0,len(df2.columns))
        Data.setups=df2

    @staticmethod
    def read_processing(ficheiro_processing):
        dfprocessing=read_csv(ficheiro_processing)   
        df3= DataFrame(data=dfprocessing)
        df3.columns = arange(0,len(df3.columns))
        Data.proctimes=df3

     
    @staticmethod    
    def read_orders(ficheiro_orders):
        dforders= read_csv(ficheiro_orders)
        df4= DataFrame(data=dforders)
        df4Sorted = df4.sort_values(by=['due'])
        Data.orders=df4

    @staticmethod 
    def initialize(ficheiro_setups, ficheiro_orders, ficheiro_processing,ficheiro_stock):
        Data.reset_Data()
        Data.read_setups(ficheiro_setups)
        Data.read_processing(ficheiro_processing)
        Data.read_orders(ficheiro_orders)
        Data.count_ops(Data.proctimes)
        Data.count_machines(Data.proctimes)
        Data.count_orders(Data.orders)
        Data.read_stock(ficheiro_stock)
        Data.mts_orders(Data.orders,Data.stocks)
        
    @staticmethod
    def count_ops(proctimes):
        Data.num_ops = len(proctimes.columns)
    
    @staticmethod
    def count_machines(proctimes):
        Data.num_machines = len(proctimes.index)
    
    @staticmethod
    def count_orders(orders):
        Data.num_orders = len(orders.index)
    
    @staticmethod
    def read_stock(ficheiro_stock):
        dfstock=read_csv(ficheiro_stock)   
        df4= DataFrame(data=dfstock)
        Data.stocks=df4

    @staticmethod
    def mts_orders(orders,stocks):
        mts = []
        for i in range(0, Data.num_orders):
            op = Data.orders.iloc[i]['product']
            due = Data.orders.iloc[i]['due']
            qtd = Data.orders.iloc[i]['quantity']
            if Data.stocks.iloc[op-1]['current'] >= qtd:
                Data.stocks.iloc[op-1]['current'] -= qtd
            else:
                mts.append({'product':op,'quantity':qtd-Data.stocks.iloc[op-1]['current'],'due':due})
                Data.stocks.iloc[op-1]['current'] = 0
        
        for i in range(Data.num_ops):
            if Data.stocks.iloc[i]['current'] < Data.stocks.iloc[i]['minn']:
                mts.append({'product':i+1,'quantity':Data.stocks.iloc[i]['maxx'] - Data.stocks.iloc[i]['current'] ,'due':99999999})
        
        Data.num_mts = len(mts)        
        Data.mts = DataFrame(mts)
        return Data.mts
