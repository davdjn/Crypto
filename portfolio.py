import pandas as pd
import coin_tools
import tools
    
class Portfolio:
    def __init__(self, input):
        '''
        input = [[coin1, amount1, price1], [coin2, amount2, price2], ...]
        '''
        time = tools.get_time()
        self.coins = {}
        self.ledger = pd.DataFrame({'Date':[],'Coin':[],'Amount':[],'Price':[],'Value':[],'Note':[]})
        for coin, amount, price in input:
            self.coins.setdefault(coin, 0)
            self.coins[coin] += amount
            self.write(time, coin, amount, price, 'init')
        self.history = [(time, self.get_total(), input)]
    
    def write(self, time, coin, amount, price, note):
        self.ledger.loc[len(self.ledger.index)] = [time, coin, amount, price, amount*price, note]
                       
    def add_coin(self, coin, amount, price=None, time=tools.get_time(), note=''):
        if price is None:
            price = coin_tools.get_price(coin)
        self.coins.setdefault(coin, 0)
        self.coins[coin] += amount
        self.write(time, coin, amount, price, note)
    
    def remove_coin(self, coin, amount, price=None, time=tools.get_time(), note=''):
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if self.coins[coin] < amount:
            raise Exception ("Not enough of the coin in the portfolio.")
        if price is None:
            price = coin_tools.get_price(coin)
        self.coins[coin] -= amount
        self.write(time, coin, -amount, price, note)
        
    def overwrite_coin_amount(self, coin, amount, price=None, time=tools.get_time()):  
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if price is None:
            price = coin_tools.get_price(coin)
        prev, self.coins[coin] = self.coins[coin], amount
        self.ledger.write(time, coin, amount - prev, price, note='overwrite')
        
    def swap(self, coin1, amount1, price1, coin2, amount2, price2=None, time=tools.get_time()):
        '''
        Swapping amount1 of coin1 for amount2 of coin2.
        '''
        if price2 is None:
            price2 = amount1 * price1 / amount2
        note = 'swap'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.add_coin(coin2, amount2, price2, time, note)
    
    def provide_liquidity(self, lp_recieved, coin1, amount1, price1, coin2, amount2, price2=None, time=tools.get_time()):
        if price2 is None:
            price2 = amount1 * price1 / amount2
        if coin1 > coin2:
            coin1, coin2 = coin2, coin1
            amount1, amount2 = amount2, amount1
        note = 'add LP'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.remove_coin(coin2, amount2, price2, time, note)
        self.add_coin('LP_'+coin1+'_'+coin2, lp_recieved, None, time, note)
        
    def remove_liquidity(self, lp_returned, coin1, amount1, price1, coin2, amount2, price2=None, time=tools.get_time()):
        if price2 is None:
            price2 = amount1 * price1 / amount2
        if coin1 > coin2:
            coin1, coin2 = coin2, coin1
            amount1, amount2 = amount2, amount1
        note = 'remove LP'
        self.remove_coin('LP_'+coin1+'_'+coin2, lp_returned, None, time, note)
        self.add_coin(coin1, amount1, price1, time, note)
        self.add_coin(coin2, amount2, price2, time, note)
        
    def get_total(self):
        return sum([coin_tools.get_coin_price(c) * self.coins[c] for c in self.coins])
        
    def get_summary(self):
        df = pd.DataFrame({ 'Coin':[],'Amount':[],'Price':[],'Value':[]})
        for c in self.coins:
            # This computation should be generalized in the future. Coin should become a class with a name and a 'get_price' function, which can be assigned at instatiation.
            # This allows for more abstract capabilities, such as including leveraged yield farming.
            price = coin_tools.get_coin_price(c)
            value = price * self.coins[c]
            df.loc[len(df.index)] = [c, self.coins[c], price, value]
        df = df.sort_values(by='Value', ascending=False)
        df.loc[len(df.index)] = ['Total', None, None, sum(df['Value'])]
        self.update_history(df)
        return df
    
    def update_history(self, df=None):
        if df is None:
            df = self.get_summary()
        df, total = df[:-1], float(df[-1:]['Value'])
        self.history.append((tools.get_time(), total, df.values.tolist()))