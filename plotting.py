import plotly.graph_objects as go
import tools

def plot_coins(coins, days, data_resolution=300):
    '''
    Plots the data for the given coins for the last x days.
    '''
    fig= go.Figure()
    fig.update_layout()
    times_utc = tools.get_even_times(days, data_resolution)[1]
    for c in coins:
        fig.add_trace(go.Scatter(x=times_utc, y=tools.get_coin_prices(c, days, data_resolution), name=c))
    fig.show()    