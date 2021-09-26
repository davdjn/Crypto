import numpy as np
import tools
from itertools import combinations

def il(pa0, pa1, pb0, pb1):
    '''
    Compute impermanent loss of providing liquidity given the prices of two assets at two points in time.
    '''
    ratio = (pa0 * pb1) / (pa1 * pb0)
    return (2 * np.sqrt(ratio) / (ratio + 1)) - 1

def il_leveraged(pa0, pa1, pb0, pb1, rate=0, leverage=1):
    '''
    Compute net profit when using leverage to provide liquidity by computing difference between impermanent loss and APY.
    Rate is the APY which accounts for leverage. The APY is computed against the lower of the initial and final values.
    '''
    ratio = (pa0 * pb1) / (pa1 * pb0)
    return leverage * il(pa0, pa1, pb0, pb1) + 2 * rate * min(1, np.sqrt(ratio)) / (ratio + 1)
    
def lp_stats(pa0, pa1, pb0, pb1, qa0):
    '''
    Prints various stats for liquidity providing.
    '''
    ratio = (pa0 * pb1) / (pa1 * pb0)
    value = pa1 * qa0 * np.sqrt(ratio)
    print("Price of A: {0:>10.2f} --> {1:<10.2f}".format(pa0, pa1))
    print("Quant of A: {0:>10.2f} --> {1:<10.2f}".format(qa0, value / pa1))
    print("Price of B: {0:>10.2f} --> {1:<10.2f}".format(pb0, pb1))
    print("Quant of B: {0:>10.2f} --> {1:<10.2f}".format((qa0 * pa0) / pb0, value / pb1))
    print("IL: {0:<10.3f}".format(il(pa0, pa1, pb0, pb1)))
    
def correlation(coins, days, data_resolution=300):
    '''
    Computes correlations between each pair of given coins in the last x days.
    '''
    values = {}
    correlation = {}   
    for c in coins:
        values[c] = tools.get_prices(c, days, data_resolution)
    for c, d in combinations(coins, 2):
        correlation[(c,d)] = np.corrcoef(values[c], values[d])[0,1]
    return correlation