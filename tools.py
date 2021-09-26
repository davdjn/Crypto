import numpy as np
import time
from datetime import datetime
from pycoingecko import CoinGeckoAPI
from bisect import bisect_left

def get_coin_data(coin, days, data_resolution=300):
    '''
    Pulls pricing data for a given coin from coinbase, evenly spaced from the last x days
    '''
    cg = CoinGeckoAPI()
    times, prices = transpose(cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days=days)['prices'])
    times = [t / 1000 for t in times]
    return time_spacing(prices, times, get_even_times(days, data_resolution)[0])
    
def get_even_times(days, data_resolution):
    '''
    For a number of days and a resolution, returns an evenly spaced timestamps from now to now - days. 
    '''
    now = time.time()
    times = np.linspace(now - days * 86400, now, data_resolution)
    return times, [datetime.utcfromtimestamp(t) for t in times]
    
def time_spacing(values, times, even_times):
    '''
    Given values and their corresponding times, as well as a list of evenly spaced times, returns a list of values most closely corresponding to each point in even_times
    '''
    even_values = []
    for t in even_times:
        index = bisect_left(times, t)
        if index == len(values):
            index -= 1
        even_values.append(values[index])
    return even_values

def transpose(arr):
    '''
    Takes an array [[1,1,1,1], [2,2,2,2], [3,3,3,3]] and returns [[1,2,3], [1,2,3], [1,2,3], [1,2,3]]
    '''
    return [[a[i] for a in arr] for i in range(len(arr[0]))]





