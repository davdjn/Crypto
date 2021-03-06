from pycoingecko import CoinGeckoAPI
import tools

class Coin:
    def __init__(self, name, coin_type='token'):
        self.name = name
        self.type = coin_type
        
    def get_price(self):
        if self.type == 'lp':
            return get_lp_token_price(self.name)
        if self.type == 'debt':
            return -get_price(self.name)
        return get_price(self.name)
        
    def __hash__(self):
        return hash((self.name, self.type))

    def __eq__(self, other):
        return (self.name, self.type) == (other.name, other.type)

    def __ne__(self, other):
        return not(self == other)
        
    def __str__(self):
        return self.name   

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
    
    