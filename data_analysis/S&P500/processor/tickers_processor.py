import yahoo_fin.stock_info as si
import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile, join

class processor :
    def __init__(self) :
        self.dow = None
        self.ftse_100 = None
        self.ftse_250 = None
        self.nasdaq = None
        self.nifty_50 = None
        self.sp500 = None
        self.other = None
        self.tickers = None
    
    def get_tickers(self) :
        self.dow = si.tickers_dow(include_company_data = True)
        self.ftse_100 = si.tickers_ftse100(include_company_data = True)
        self.ftse_250 = si.tickers_ftse250(include_company_data = True)
        self.nasdaq = si.tickers_nasdaq(include_company_data = True)
        self.nifty_50 = si.tickers_nifty50(include_company_data = True)
        self.other = si.tickers_other(include_company_data = True)
        self.sp500 = si.tickers_sp500(include_company_data = True)
        self.__process_tickers()
        return self.tickers
        
    def __process_tickers(self) :
        dow_tickers_df = self.dow[['Company', 'Symbol']]

        ftse_100_tickers_df = self.ftse_100[['Company','EPIC']]
        ftse_100_tickers_df.columns = ['Company','Symbol']

        ftse_250_tickers_df = self.ftse_250
        ftse_250_tickers_df.columns = ['Company','Symbol']

        nasdaq_tickers_df = self.nasdaq[['Security Name','Symbol']]
        nasdaq_tickers_df.columns = ['Company','Symbol']

        nifty_50_tickers_df = self.nifty_50[['Company Name','Symbol']]
        nifty_50_tickers_df.columns = ['Company','Symbol']

        other_tickers_df = self.other[['Security Name','ACT Symbol']]
        other_tickers_df.columns = ['Company','Symbol']

        sp500_tickers_df = self.sp500[['Security','Symbol']]
        sp500_tickers_df.columns = ['Company','Symbol']

        self.tickers = pd.concat([dow_tickers_df, ftse_100_tickers_df, ftse_250_tickers_df, nasdaq_tickers_df, nifty_50_tickers_df, other_tickers_df, sp500_tickers_df], ignore_index=True)
        
    def save_tickers_in_csv(self, file_name) :
        self.tickers.to_csv('data/' + file_name + '.csv', index = False)
        
    def get_historical_data(self, ticker_lst, tickers_with_L = False) :
        processed = self.__get_processed_tickers()
        tickers_no_processed = []

        for ticker in ticker_lst :
            if ticker not in processed :
                try : 
                    if tickers_with_L :
                        ticker = ticker + ".L"
                    historical = si.get_data(ticker, index_as_date = True, interval = "1d")
                    df = pd.DataFrame(historical, columns = ['close'])
                    df.columns = [ticker]
                    ticker = ticker.replace('.','#')
                    df.to_csv('data/' + ticker + '.csv', index = True)
                except AssertionError :
                    tickers_no_processed.append(ticker)
                    print(f'{ticker} not processed')
                except KeyError :
                    tickers_no_processed.append(ticker)
                    print(f'{ticker} not processed')
                except TypeError :
                    tickers_no_processed.append(ticker)
                    print(f'{ticker} not processed')
                except JSONDecodeError :
                    tickers_no_processed.append(ticker)
                    print(f'{ticker} not processed')
        
        return tickers_no_processed
    
    def __get_processed_tickers(self) :
        tickers = [f for f in listdir('data') if isfile(join('data', f))]
        for ticker in tickers :
            ticker = ticker.replace('#','.')
        return tickers