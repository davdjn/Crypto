import plotly.graph_objects as go
import tools
import coin_tools

def plot_coins(coins, days, data_resolution=300):
    '''
    Plots the data for the given coins for the last x days.
    '''
    fig = go.Figure()
    fig.update_layout(template="plotly_dark")
    times_utc = tools.get_even_times(days, data_resolution)[1]
    for c in coins:
        fig.add_trace(go.Scatter(x=times_utc, y=coin_tools.get_prices(c, days, data_resolution), name=c))
    fig.show()
    
def plot_portfolio(portfolio, metric):
    key = {'amount' : 1, 'price' : 2, 'value' : 3}
    data = portfolio.pivot_history()
    sorted_coins = sorted(portfolio.coins, key=lambda c: data[c][key[metric]][-1], reverse=True)
    
    fig = go.Figure()
    fig.update_layout(title=metric, template="plotly_dark", width=1000)
    if metric == 'value':
        fig.add_trace(go.Scatter(x=data['total'][0], y=data['total'][1], name='total'))
    for c in sorted_coins:
        fig.add_trace(go.Scatter(x=data[c][0], y=data[c][key[metric]], name=c.name+'_'+c.type))
    fig.show()