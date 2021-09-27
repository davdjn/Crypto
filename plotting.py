import plotly.graph_objects as go
import tools
import coin_tools

def plot_coins(coins, days, data_resolution=300):
    '''
    Plots the data for the given coins for the last x days.
    '''
    fig = go.Figure()
    fig.update_layout()
    times_utc = tools.get_even_times(days, data_resolution)[1]
    for c in coins:
        fig.add_trace(go.Scatter(x=times_utc, y=coin_tools.get_prices(c, days, data_resolution), name=c))
    fig.show()
    
def plot_history_value(portfolio):
    data = portfolio.pivot_history()
    fig = go.Figure()
    fig.update_layout()
    fig.add_trace(go.Scatter(x=data['total'][0], y=data['total'][1], name='total value'))
    for c in portfolio.coins:
        temp = data[c]
        fig.add_trace(go.Scatter(x=temp[0], y=temp[3], name=c+' value'))
    fig.show()