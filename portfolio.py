import pandas as pd
from datetime import date
import tools

class Ledger:
    def __init__(self):
        self.df = pd.DataFrame({'Date':[],'Coin':[],'Amount':[],'Value':[],'Note':[]})
        
    def save_pickle(self, path):
        self.ledger.to_pickle(path)
    
    def load_pickle(self, path):
        self.ledger = pd.read_pickle(path)
        
    def write(self, date, coin, amount, value, note):
        self.df.loc[len(self.df.index)] = [date, coin, amount, value, note]
    
class Portfolio:
    def __init__(self, coins, amounts, values, ledger):
        self.coins = {}
        self.ledger = ledger
        time = date.today()
        if not self.ledger.df.empty:
            for row in self.ledger.df.itertuples(index=False,name=None):
                c = row[1]
                self.coins.setdefault(c, 0)
                self.coins[c] += row[2]
        for i, c in enumerate(coins):
            self.coins.setdefault(c, 0)
            self.coins[c] += amounts[i]
            self.ledger.write(time, c, amounts[i], values[i], 'Init')
                       
    def add_coin(self, coin, amount, value, time=date.today(), note=''):
        self.coins.setdefault(coin, 0)
        self.coins[coin] += amount
        self.ledger.write(time, coin, amount, value, note)
    
    def remove_coin(self, coin, amount, value, time=date.today(), note=''):
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if self.coins[coin] < amount:
            raise Exception ("Not enough of the coin in the portfolio.")
        self.coins[coin] -= amount
        self.ledger.write(time, coin, -amount, value, note)
        
    def swap(self, coin1, amount1, value1, coin2, amount2, value2=None, time=date.today()):
        '''
        Swapping amount1 of coin1 for amount2 of coin2.
        '''
        if value2 is None:
            value2 = amount1 * value1 / amount2
        self.remove_coin(coin1, amount1, value1, time, note='Swap')
        self.add_coin(coin2, amount2, value2, time, note='Swap')
    
    def provide_liquidity(self, lp_recieved, coin1, amount1, value1, coin2, amount2, value2=None, time=date.today()):
        if value2 is None:
            value2 = amount1 * value1 / amount2
        if coin1 > coin2:
            coin1, coin2 = coin2, coin1
            amount1, amount2 = amount2, amount1
        note = 'add LP'
        self.remove_coin(coin1, amount1, value1, time, note)
        self.remove_coin(coin2, amount2, value2, time, note)
        self.add_coin('LP_'+coin1+'_'+coin2, lp_recieved, None, time, note)
        
    def remove_liquidity(self, lp_returned, coin1, amount1, value1, coin2, amount2, value2=None, time=date.today()):
        if value2 is None:
            value2 = amount1 * value1 / amount2
        if coin1 > coin2:
            coin1, coin2 = coin2, coin1
            amount1, amount2 = amount2, amount1
        note = 'remove LP'
        self.remove_coin('LP_'+coin1+'_'+coin2, lp_returned, None, time, note)
        self.add_coin(coin1, amount1, value1, time, note)
        self.add_coin(coin2, amount2, value2, time, note)
        
    def get_value(self):
        total = 0
        for c in self.coins:
            if c.startswith('LP_'):
                _, coin1, coin2 = c.split('_')
                total += tools.get_lp_token_price(coin1, coin2) * self.coins[c]
            else:
                total += tools.get_price(c) * self.coins[c]
        return total