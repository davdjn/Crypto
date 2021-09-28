import pandas as pd
import pickle
import coin_tools
import tools

class Portfolio:
    def __init__(self, ledger=None, history=None):              
        self.coins = {}
        self.history = {}
        self.ledger = pd.DataFrame({'Date':[],'Coin':[],'Amount':[],'Price':[],'Value':[],'Note':[]})
    
    def save(self, ledger_path='ledger.pickle', history_path='history.pickle'):
        self.ledger.to_pickle(ledger_path)
        with open(history_path, 'wb') as f:
            pickle.dump(self.history, f)
            
    def load(self, ledger_path='ledger.pickle', history_path='history.pickle'):
        self.ledger = pd.read_pickle(ledger_path)
        with open(history_path, 'rb') as f:
            self.history = pickle.load(f)
        for row in self.ledger.itertuples(index=False,name=None):
            c = row[1]
            self.coins.setdefault(c, 0)
            self.coins[c] += row[2]
        self.update_history()
    
    def write(self, time, coin, amount, price, note):
        self.ledger.loc[len(self.ledger.index)] = [time, coin, amount, price, amount*price, note]
                       
    def add_coin(self, coin, amount, price=None, time=None, note=''):
        if time is None:
            time = tools.get_time()
        if price is None:
            price = coin_tools.get_coin_price(coin)
        self.coins.setdefault(coin, 0)
        self.coins[coin] += amount
        self.write(time, coin, amount, price, note)
    
    def remove_coin(self, coin, amount, price=None, time=None, note=''):
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if self.coins[coin] < amount:
            raise Exception ("Not enough of the coin in the portfolio.")
        if time is None:
            time = tools.get_time()
        if price is None:
            price = coin_tools.get_coin_price(coin)
        self.coins[coin] -= amount
        self.write(time, coin, -amount, price, note)
        
    def overwrite_coin_amount(self, coin, amount, price=None, time=None):  
        if coin not in self.coins:
            raise Exception("Coin is not in portfolio.")
        if time is None:
            time = tools.get_time()
        if price is None:
            price = coin_tools.get_coin_price(coin)
        prev, self.coins[coin] = self.coins[coin], amount
        self.ledger.write(time, coin, amount - prev, price, note='overwrite')
        
    def swap(self, coin1, amount1, price1, coin2, amount2, price2=None, time=None):
        '''
        Swapping amount1 of coin1 for amount2 of coin2.
        '''
        if time is None:
            time = tools.get_time()
        if price2 is None:
            price2 = amount1 * price1 / amount2
        note = 'swap'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.add_coin(coin2, amount2, price2, time, note)
    
    def provide_liquidity(self, lp_recieved, coin1, amount1, price1, coin2, amount2, price2=None, time=None):
        if time is None:
            time = tools.get_time()
        if price2 is None:
            price2 = amount1 * price1 / amount2
        if coin1 > coin2:
            coin1, coin2 = coin2, coin1
            amount1, amount2 = amount2, amount1
        note = 'add LP'
        self.remove_coin(coin1, amount1, price1, time, note)
        self.remove_coin(coin2, amount2, price2, time, note)
        self.add_coin('LP_'+coin1+'_'+coin2, lp_recieved, None, time, note)
        
    def remove_liquidity(self, lp_returned, coin1, amount1, price1, coin2, amount2, price2=None, time=None):
        if time is None:
            time = tools.get_time()
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
        
    def get_summary(self, update=True):
        df = pd.DataFrame({ 'Coin':[],'Amount':[],'Price':[],'Value':[]})
        for c in self.coins:
            price = coin_tools.get_coin_price(c)
            df.loc[len(df.index)] = [c, self.coins[c], price, self.coins[c] * price]
        df = df.sort_values(by='Value', ascending=False)
        df.loc[len(df.index)] = ['Total', None, None, sum(df['Value'])]
        if update:
            self.update_history(df)
        return df
    
    def update_history(self, df=None):
        '''
        One can update this history without creating the dataframe, but this allows reducing the number of get_coin_price calls.
        '''
        if df is None:
            df = self.get_summary()
        df, total = df[:-1], float(df[-1:]['Value'])
        history = {}
        for row in df.itertuples():
            _, coin, amount, price, _ = row
            history[coin] = (amount, price)
        history['total'] = total
        self.history[tools.get_time()] = history
        
    def pivot_history(self):
        '''
        Change formatting for easy plotting.
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