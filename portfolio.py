import pandas as pd
from datetime import date
import tools

class Ledger:
    def __init__(self):
        self.df = pd.DataFrame({'Date':[],'Coin':[],'Amount':[],'Price':[],'Value':[],'Note':[]})
        
    def save_pickle(self, path):
        self.ledger.to_pickle(path)
    
    def load_pickle(self, path):
        self.ledger = pd.read_pickle(path)
        
    def write(self, time, coin, amount, price, note):
        self.df.loc[len(self.df.index)] = [time, coin, amount, price, amount*price, note]
        
    def get_amount(self, coin):
        return sum(self.df[self.df['Coin'].str.contains(coin)]['Amount'])
    
class Portfolio:
    def __init__(self, input, ledger):
        '''
        input = [[coin1, amount1, price1], [coin2, amount2, price2], ...]
        '''
        self.coins = {}
        self.ledger = ledger
        time = date.today()
        if not self.ledger.df.empty:
            for row in self.ledger.df.itertuples(index=False,name=None):
                c = row[1]
                self.coins.setdefault(c, 0)
                self.coins[c] += row[2]
        for c in input:
            coin, amount, price = c
            self.coins.setdefault(coin, 0)
            self.coins[coin] += amount
            self.ledger.write(time, coin, amount, price, 'init')
                       
    def add_coin(self, coin, amount, price, time=date.today(), note=''):
        self.coins.setdefault(coin, 0)
        self.coins[coin] += amount
        self.ledger.write(time, coin, amount, price, note)
    
    def remove_coin(self, coin, amount, price, time=date.today(), note=''):
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if self.coins[coin] < amount:
            raise Exception ("Not enough of the coin in the portfolio.")
        self.coins[coin] -= amount
        self.ledger.write(time, coin, -amount, price, note)
        
    def overwrite_coin_amount(self, coin, amount, price, time=date.today(), note=''):
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        self.coins[coin] = amount
        led_amount = self.ledger.get_amount(coin)
        self.ledger.write(time, coin, amount - led_amount, price, note='overwrite')
        
    def swap(self, coin1, amount1, price1, coin2, amount2, price2=None, time=date.today()):
        '''
        Swapping amount1 of coin1 for amount2 of coin2.
        '''
        if price2 is None:
            price2 = amount1 * price1 / amount2
        note = 'swap'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.add_coin(coin2, amount2, price2, time, note)
    
    def provide_liquidity(self, lp_recieved, coin1, amount1, price1, coin2, amount2, price2=None, time=date.today()):
        if price2 is None:
            price2 = amount1 * price1 / amount2
        if coin1 > coin2:
            coin1, coin2 = coin2, coin1
            amount1, amount2 = amount2, amount1
        note = 'add LP'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.remove_coin(coin2, amount2, price2, time, note)
        self.add_coin('LP_'+coin1+'_'+coin2, lp_recieved, None, time, note)
        
    def remove_liquidity(self, lp_returned, coin1, amount1, price1, coin2, amount2, price2=None, time=date.today()):
        if price2 is None:
            price2 = amount1 * price1 / amount2
        if coin1 > coin2:
            coin1, coin2 = coin2, coin1
            amount1, amount2 = amount2, amount1
        note = 'remove LP'
        self.remove_coin('LP_'+coin1+'_'+coin2, lp_returned, None, time, note)
        self.add_coin(coin1, amount1, price1, time, note)
        self.add_coin(coin2, amount2, price2, time, note)
        
    def get_value(self):
        total = 0
        for c in self.coins:
            if c.startswith('LP_'):
                _, coin1, coin2 = c.split('_')
                total += tools.get_lp_token_price(coin1, coin2) * self.coins[c]
            else:
                total += tools.get_price(c) * self.coins[c]
        return total
        
    def get_summary(self):
        df = pd.DataFrame({ 'Coin':[],'Amount':[],'Price':[],'Value':[]})
        total = 0
        for c in self.coins:
            if c.startswith('LP_'):
                _, coin1, coin2 = c.split('_')
                price = tools.get_lp_token_price(coin1, coin2)
                value = price * self.coins[c]
            else:
                price = tools.get_price(c)
                value = price * self.coins[c]
            total += value
            df.loc[len(df.index)] = [c, self.coins[c], price, value]
        df = df.sort_values(by='Value', ascending=False)
        df.loc[len(df.index)] = ['Total', '', '', total]
        return df