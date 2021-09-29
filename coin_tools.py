from pycoingecko import CoinGeckoAPI
import tools

def get_price(coin):
    '''
    Pulls pricing data for a given coin from coinbase.
    '''
    cg = CoinGeckoAPI()
    return cg.get_price(ids=coin, vs_currencies='usd')[coin]['usd']
    
def get_prices(coin, days, data_resolution=300):
    '''
    Pulls pricing data for a given coin from coinbase, evenly spaced from the last x days.
    '''
    cg = CoinGeckoAPI()
    times, prices = tools.transpose(cg.get_coin_market_chart_by_id(id=coin, vs_currency='usd', days=days)['prices'])
    times = [t / 1000 for t in times]
    return tools.time_spacing(prices, times, tools.get_even_times(days, data_resolution)[0])
    
def get_lp_token_price(coin):
    '''
    Placeholder. This is function is pretty hard to implement.
    '''
    price = float(input("Price of " + coin + ": "))
    print('LP token price for', coin + ':', price)
    return price
    
def get_coin_price(coin):
    if coin.startswith('LP_'):
        return get_lp_token_price(coin)
    return get_price(coin)