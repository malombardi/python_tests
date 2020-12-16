import pandas as pd
import matplotlib.pyplot as plt
import file_manipulation as fm
import data_calculations as dc

def plot_values(df):
    df.reset_index(drop=False, inplace=True)
    aggregation_functions = {'Fecha': 'first','NP':'mean', 'FTP': 'first', 'IF':'mean', 'Seconds':'sum', 'TSS':'sum', 'Fatigue':'mean','Fitness':'mean','Freshness':'mean'}
    df = df.groupby(df['Fecha']).aggregate(aggregation_functions)

    plt.figure(figsize=(18,4))
    plt.plot_date(df['Fecha'], df['Fitness'], '.-', label='Fitness')
    plt.plot_date(df['Fecha'], df['Fatigue'], '.-', label='Fatigue')
    plt.plot_date(df['Fecha'], df['Freshness'], '.-', label='Freshness')

    plt.legend(loc='upper left')
    x = range(df.shape[0])
    plt.xticks(x, df.Fecha)
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=90)
    plt.grid()
    plt.show()

def main():
    df_origin, df_dest = fm.get_data_from_files()
    df_origin = dc.start_calculations(df_origin, df_dest)

    column_names = ['Fecha', 'NP', 'FTP', 'IF', 'Seconds', 'TSS', 'Fatigue', 'Fitness', 'Freshness']
    df_origin = df_origin[column_names]
    
    fm.save_df_to_csv(df_origin)
    
    plot_values(df_origin)

if __name__ == "__main__":
    main()
