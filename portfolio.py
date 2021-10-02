import pandas as pd
import pickle
import coin_tools
import tools

class Portfolio:
    def __init__(self):              
        self.coins = {}
        self.history = {}
        self.ledger = pd.DataFrame({'Date':[],'Coin':[],'Type':[],'Amount':[],'Price':[],'Value':[],'Note':[]})
    
    def save(self, path='portfolio.pickle'):
        with open('pickles/' + path, 'wb') as f:
            pickle.dump(self, f)
            
    def load(self, path='portfolio.pickle'):
        with open('pickles/' + path, 'rb') as f:
            load = pickle.load(f)
        self.coins, self.history, self.ledger = load.coins, load.history, load.ledger
    
    def write(self, time, coin, amount, price, note):
        self.ledger.loc[len(self.ledger.index)] = [time, coin.name, coin.type, amount, price, amount*price, note]
                       
    def add_coin(self, coin, amount, price=None, time=None, note=''):
        if time is None:
            time = tools.get_time()
        if price is None:
            price = coin.get_price()
        self.coins.setdefault(coin, 0)
        self.coins[coin] += amount
        self.write(time, coin, amount, price, note)
    
    def remove_coin(self, coin, amount, price=None, time=None, note=''):
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if self.coins[coin] < amount:
            choice = input('Warning: Not enough ' + coin + ' in your portfolio. Input (n) to terminate.')
            if choice == 'n':
                raise Exception ("Not enough " + coin + " in your portfolio.")
        if time is None:
            time = tools.get_time()
        if price is None:
            price = coin.get_price()
        self.coins[coin] -= min(self.coins[coin], amount)
        self.write(time, coin, -amount, price, note)
        
    def overwrite_coin_amount(self, coin, amount, price=None, time=None):  
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if time is None:
            time = tools.get_time()
        if price is None:
            price = coin.get_price()
        prev, self.coins[coin] = self.coins[coin], amount
        self.ledger.write(time, coin, amount - prev, price, note='overwrite')
        
    def swap(self, coin1, coin2, amount1, amount2, price1=None, price2=None, time=None):
        '''
        Swapping amount1 of coin1 for amount2 of coin2.
        '''
        if time is None:
            time = tools.get_time()
        if price1 is None:
            price1 = coin1.get_price()
        if price2 is None:
            price2 = amount1 * price1 / amount2
        note = 'swap'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.add_coin(coin2, amount2, price2, time, note)
    
    def add_liquidity(self, lp_coin, lp_recieved, coin1, coin2, amount1, amount2, price1=None, price2=None, time=None):
        if time is None:
            time = tools.get_time()
        if price1 is None:
            price1 = coin1.get_price()
        if price2 is None:
            price2 = amount1 * price1 / amount2
        note = 'add LP'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.remove_coin(coin2, amount2, price2, time, note)
        self.add_coin(lp_coin, lp_recieved, None, time, note)
        
    def remove_liquidity(self, lp_coin, lp_returned, coin1, coin2, amount1, amount2, price1=None, price2=None, time=None):
        if time is None:
            time = tools.get_time()
        if price1 is None:
            price1 = coin1.get_price()
        if price2 is None:
            price2 = amount1 * price1 / amount2
        note = 'remove LP'
        self.remove_coin(lp_coin, lp_returned, None, time, note)
        self.add_coin(coin1, amount1, price1, time, note)
        self.add_coin(coin2, amount2, price2, time, note)          
        
    def get_summary(self, update=False):
        df = pd.DataFrame({'Coin':[],'Type':[],'Amount':[],'Price':[],'Value':[]})
        if update or not self.history:
            self.update_history()          
        last = list(self.history.keys())[-1]
        for c in self.coins:
            if not c in self.history[last]:
                self.update_history()
                last = list(self.history.keys())[-1]
            price = self.history[last][c][1]
            df.loc[len(df.index)] = [c.name, c.type, self.coins[c], price, self.coins[c] * price]
        df.sort_values(by='Value', ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.loc[len(df.index)] = ['Total', '', None, None, sum(df['Value'])]  
        return df
        
    def clear_dust(self, threshold=.001):
        coins = list(self.coins.keys())
        for c in coins:
            if self.coins[c] < threshold:
                self.coins.pop(c)
    
    def update_history(self):
        history = {}
        total = 0
        for coin in self.coins:
            amount = self.coins[coin]
            price = coin.get_price()
            history[coin] = (amount, price)
            total += amount * price
        history['total'] = total
        self.history[tools.get_time()] = history
        
    def pivot_history(self):
        '''
        Change history formatting for easy plotting.
        '''
        history = self.history
        data = {'total' : [[], []]}

        for date in history:
            for coin in self.coins:
                if coin in history[date]:
                    data.setdefault(coin, [[],[],[],[]])
                    amount, price = history[date][coin]
                    data[coin][0].append(date)
                    data[coin][1].append(amount)
                    data[coin][2].append(price)
                    data[coin][3].append(price * amount)
            data['total'][0].append(date)
            data['total'][1].append(history[date]['total'])
        return data