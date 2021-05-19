import tickers_processor as tp
import pandas as pd
import numpy as np

def main():
    processor = tp.processor()
    tickers_df = processor.get_tickers()

    processor.save_tickers_in_csv('companies')

    tickers_lst =  tickers_df['Symbol'].tolist()
    tickers_no_processed = processor.get_historical_data(tickers_lst)

    tickers_no_processed = processor.get_historical_data(tickers_no_processed, tickers_with_L = True)

    print(tickers_no_processed)
    
    
if __name__ == "__main__":
    main()
