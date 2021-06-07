import numpy as np
import pandas as pd
import cupy as cp
import time
from loguru import logger
from cupy import inf
from os import listdir
from os.path import isfile, join

def read_df_return_cp(file):
    logger.info("read and return - START")
    logger.info(file)
    df = pd.read_csv(file, index_col='Fecha', parse_dates=True)
    df = df.iloc[3:]
    df = df[::-1]
    df_columns = df.columns.tolist()
    cu_data = cp.asarray(df.to_numpy().T)
    cp.cuda.Stream.null.synchronize()
    logger.info("read and return - END")
    return cu_data, df_columns

def calculate_pct(cp_array):
    logger.info("PCT - START")
    [cols, rows] = cp_array.shape
    cp.cuda.Stream.null.synchronize()
    cp_array_1 = cp_array[:, 1:]
    cp_array_zeros = cp.zeros((cp_array.shape[0],1), dtype='float64')
    cp_array_concat = cp.concatenate((cp_array_1,cp_array_zeros), axis=1)
    cp_pct = cp.log(cp_array_concat/cp_array)
    cp_pct[cp_pct == -inf] = 0
    cp_pct = cp.nan_to_num(cp_pct)
    cp.cuda.Stream.null.synchronize()
    logger.info("PCT - END")
    return cp_pct

def calculate_variance(cp_array):
    '''
    THIS NEEDS calculate_pct TO WORK AND PASS THE RESULT TO THIS METHOD
    '''
    logger.info("Variance - START")
    cp_var = cp.var(cp_array.T, axis=1)
    cp.cuda.Stream.null.synchronize()
    logger.info("Variance - END")
    return cp_var

def calculate_covariance(cp_array):
    '''
    THIS NEEDS calculate_pct TO WORK AND PASS THE RESULT TO THIS METHOD
    '''
    logger.info("Covariance - START")
    cp_cov = cp.cov(cp_array)
    cp.cuda.Stream.null.synchronize()
    logger.info("Covariance - END")
    return cp_cov

def calculate_correlation(cp_array):
    '''
    THIS NEEDS calculate_pct TO WORK AND PASS THE RESULT TO THIS METHOD
    '''
    logger.info("Correlation - START")
    cp_corr = cp.corrcoef(cp_array)
    cp.cuda.Stream.null.synchronize()
    logger.info("Correlation - END")
    return cp_corr

def calculate_anual_expected_return(cp_array):
    '''
    THIS NEEDS calculate_pct TO WORK AND PASS THE RESULT TO THIS METHOD
    '''
    logger.info("Expected return - START")
    cp_er = cp.mean(cp_array.T[-250:],axis=0)*250
    cp_er = cp.nan_to_num(cp_er)
    cp.cuda.Stream.null.synchronize()
    logger.info("Expected return - END")
    return cp_er

def calculate_anual_volatility(cp_array):
    '''
    THIS NEEDS calculate_pct TO WORK AND PASS THE RESULT TO THIS METHOD
    '''
    logger.info("Volatility - START")
    cp_volatility = cp.zeros(cp_array.shape[0], dtype='float64')
    cp.cuda.Stream.null.synchronize()
    for x in range(cp_array.shape[0]):
        cp_volatility[x] = cp_array[x].std() * cp.sqrt(250)
    cp.cuda.Stream.null.synchronize()
    logger.info("Volatility - END")
    return cp_volatility

def calculate_efficient_frontier(cp_array, cp_er, cp_cov):
    logger.info("Efficient frontier - START")
    num_assets = cp_array.shape[0]
    num_portfolios = 10000
    
    p_ret = [] # Define an empty array for portfolio returns
    p_vol = [] # Define an empty array for portfolio volatility
    p_weights = [] # Define an empty array for asset weights
    
    cp_cov = cp.nan_to_num(cp_cov)
    cp_er = cp.nan_to_num(cp_er)
    
    cp.cuda.Stream.null.synchronize()
    for portfolio in range(num_portfolios):
        choices = cp.random.choice(2, num_assets)
        weights = cp.random.choice(choices, num_assets)
        weights = weights.astype(cp.float64)
        indices = cp.nonzero(weights)
        val = cp.random.random(len(indices[0]))
        cp.put(weights, indices[0], val)
        weights = weights/cp.sum(weights)
        p_weights.append(weights)
        returns = cp.dot(weights, cp_er) #
        p_ret.append(returns.item())
        var = cp.sum(cp.multiply((cp.multiply(cp_cov, weights)), weights))
        sd = cp.sqrt(var)
        ann_sd = sd*cp.sqrt(250)
        p_vol.append(ann_sd.item())
    
    cp.cuda.Stream.null.synchronize()

    data = {'Returns':p_ret, 'Volatility':p_vol}
    logger.info("Efficient frontier - END")
    return data, p_weights

def get_portfolios(columns_list, data_in, p_weights):
    logger.info("Portfolios - START")
    
    for counter, symbol in enumerate(columns_list):
        data_in[symbol+' weight'] = [w[counter].item() for w in p_weights]
    
    portfolios  = pd.DataFrame(data_in)
    #min_vol_port = cp.where(data_in['Volatility'] == cp.amax(data_in['Volatility']))
    min_vol_port = portfolios.iloc[portfolios['Volatility'].idxmin()]    
    Rf=4
    annRiskFreeRate = Rf/100
    rf = (np.power((1 + annRiskFreeRate),  (1.0 / 360.0)) - 1.0) * 100 
    #rf = 0.01 # risk factor
    optimal_risky_port = portfolios.iloc[((portfolios['Returns']-rf)/portfolios['Volatility']).idxmax()]
    logger.info("Portfolios - END")
    return min_vol_port, optimal_risky_port

def main():
    logger.add("portfolio_optim.log")

    dir = 'data_shuffle'
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    
    for file in files :
        path = dir + '/' + file
        [data, columns_list] = read_df_return_cp(path)
        pct = calculate_pct(data)
        variance = calculate_variance(pct)
        covariance = calculate_covariance(pct)
        correlation = calculate_correlation(pct)
        expected_return = calculate_anual_expected_return(pct)
        volatility = calculate_anual_volatility(pct)
        [efficient_frontier, wheights] = calculate_efficient_frontier(data, expected_return, covariance)
    
        [min_volatility_portfolio, optimal_risky_portfolio] = get_portfolios(columns_list, efficient_frontier,wheights)
        logger.info("Min volatility portfolio")
        logger.info("\n" + min_volatility_portfolio.to_string())
        logger.info("Optimal portfolio")
        logger.info("\n" + optimal_risky_portfolio.to_string())
    
if __name__ == "__main__":
    main()






