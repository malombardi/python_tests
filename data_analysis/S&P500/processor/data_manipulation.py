import pandas as pd
import numpy as np
import random
import math
import threading
import progress_bar as progressBar

def FillMissingValues(df_todo):
    print_console("FillMissingValues")
    for step in df_todo.columns:
        df_todo[step] = df_todo[step].fillna(0)
    return df_todo

def Read():
    print_console("READ")
    #Read the data
    df_todo = pd.read_csv('last_four_years_fill.csv', index_col='Fecha')
    
    return df_todo
    
def Shuffle(lst):
    random.shuffle(lst)
    
def save_file(df, step_shuffle, step_processing):
    file_name = 'data_shuffle/companies_' + str(step_shuffle) + '_' + str(step_processing) + '.csv'
    print_console("SAVE FILE: " + file_name)
    df.reset_index(level=0, inplace=True)
    df.rename(columns={"index": "Fecha"}, inplace=True)
    df.to_csv(file_name, index = False)
    
def ProcessData(companies_lst, df_todo, step_shuffle):
    prev_step = 0
    
    for step in range(300,len(companies_lst), 300) :
        comp_lst = companies_lst[prev_step:step]
            
        df = df_todo[comp_lst]

        save_file(df, step_shuffle, prev_step)
        prev_step = step
            
def print_console(text):
    print("--------- " + str(text) + " ---------")
    
def main() :
    df_todo = Read()
    
    #df_todo = FillMissingValues(df_todo)
    
    #df = df_todo.copy()
    #df.reset_index(level=0, inplace=True)
    #df.rename(columns={"index": "Fecha"}, inplace=True)
    #df.to_csv('last_four_years_fill.csv', index = False)
    
    companies_lst = df_todo.columns.values
    
    for step_shuffle in range(80):
        Shuffle(companies_lst)
        ProcessData(companies_lst, df_todo, step_shuffle)
    
if __name__ == "__main__":
    main()