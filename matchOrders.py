import re
from operator import itemgetter

def matchOrders(ordersPool):

    sybmolSortedLst = sorted([(ordersPool[i]['sender'],ordersPool[i]['symbol'],ordersPool[i]['send'],ordersPool[i]['get'],\
                           ordersPool[i]['price'],)\
                          for i in range(len(ordersPool))], key=itemgetter(1, 2))

    mathchedOrders = []
    for i in range(len(sybmolSortedLst)-1):
        if (sybmolSortedLst[i][2] == sybmolSortedLst[i+1][3]) and (sybmolSortedLst[i][3] == sybmolSortedLst[i+1][2]) :

            # Split symbol and define direction and price matching
            splittedSymbol1 = re.split(r'/', sybmolSortedLst[i][1])[0]
            splittedSymbol2 = re.split(r'/', sybmolSortedLst[i+1][1])[0]

            if ((splittedSymbol1 == sybmolSortedLst[i][2] and splittedSymbol2 == sybmolSortedLst[i+1][3]) \
                and (sybmolSortedLst[i][-1] <= sybmolSortedLst[i+1][-1])) \
                or ((splittedSymbol1 == sybmolSortedLst[i][3] and splittedSymbol2 == sybmolSortedLst[i+1][2])\
                   and (sybmolSortedLst[i][-1] >= sybmolSortedLst[i+1][-1])):

                mathchedOrders.append((sybmolSortedLst[i], sybmolSortedLst[i+1],))

    return mathchedOrders
