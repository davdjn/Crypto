import numpy as np
import pandas as pd
import time
from datetime import datetime
from bisect import bisect_left

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
    
def print_df(df):
    print(df.tail(12).to_string(float_format=lambda x: "{:.2f}".format(x)), '\n')

def get_time(time=None):
    if time is None:
        time = datetime.now()
    return f'{time:%y-%m-%d %H:%M}'

