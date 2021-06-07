import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join    
import progress_bar as progressBar

class file_processor:
    def __init__(self) :
        self.tickers_df = None
        
    def get_tickers(self, dir_name, counter_size, dir_dest, file_prefix, is_first_process=False) :
        if not dir_dest == '.' and not os.path.exists(dir_dest):
            os.makedirs(dir_dest)
        tickers = [f for f in listdir(dir_name) if isfile(join(dir_name, f))]
        counter = 0
        file_count = 0
        for ticker in progressBar.progressBar(tickers, prefix = 'Progress:', suffix = 'Complete', length = 50):
            if is_first_process :
                df = pd.read_csv(dir_name + '/' + ticker)
                str_ticker = ticker.split('.csv')[0]
                df.columns = ['Fecha',str_ticker]
                df.set_index('Fecha', inplace=True)
            else :
                df = pd.read_csv(dir_name + '/' + ticker, index_col='Fecha')
                
            if self.tickers_df is None:
                self.tickers_df = df.copy()
            else:
                if df.shape[0] > self.tickers_df.shape[0] :
                    self.tickers_df = df.join(self.tickers_df)
                else :
                    self.tickers_df = self.tickers_df.join(df)
            
            counter +=1
            
            if counter == counter_size :
                counter = 0
                self.tickers_df.reset_index(level=0, inplace=True)
                self.tickers_df.rename(columns={"index": "Fecha"}, inplace=True)
                self.tickers_df.to_csv(dir_dest + '/' + file_prefix + str(file_count) + '.csv', index = False)
                self.tickers_df = None
                file_count += 1
        
        if counter > 0 :
            self.tickers_df.reset_index(level=0, inplace=True)
            self.tickers_df.rename(columns={"index": "Fecha"}, inplace=True)
            self.tickers_df.to_csv(dir_dest + '/' + file_prefix + str(file_count) + '.csv', index = False)
            self.tickers_df = None
                
def main():
    fp = file_processor()
    fp.get_tickers( dir_name='data', counter_size=100, dir_dest='closed' , file_prefix='closed', is_first_process=True)
    fp.get_tickers( dir_name='closed', counter_size=10, dir_dest='closed_v2' , file_prefix='closed')
    fp.get_tickers( dir_name='closed_v2', counter_size=4, dir_dest='closed_v3' , file_prefix='closed')
    fp.get_tickers( dir_name='closed_v3', counter_size=3, dir_dest='.' , file_prefix='final')
    
if __name__ == "__main__":
    main()
