import pandas as pd
import math

def get_between_dates(df_origin, df_dest):
    begin_date = ''
    if df_origin.shape[0] > 0:
        begin_date = df_origin['Fecha'][df_origin.shape[0]-1]
    else:
        begin_date = '2020-10-11'
    end_date = df_dest['Fecha'][0]
    df = pd.DataFrame({'Fecha':pd.date_range(begin_date, end_date)})
    df = df[1:]
    return df

def merge_dfs(df_dest, df_dates_between):
    df_merged = df_dates_between.merge(df_dest, on='Fecha', how='left')
    df_merged['NP']=df_merged['NP'].fillna(0)
    df_merged['Tiempo']=df_merged['Tiempo'].fillna('0:0:0')

    return df_merged

def set_ftp(ftp, df):
    ftp_array=[]
    for i in range(df.shape[0]):
        ftp_array.append(ftp)
    df['FTP'] = ftp_array
    df.NP = df.NP.astype(int)

def calculate_intensity_factor(df):
    intensity_factor = df.NP/df.FTP
    df['IF'] = intensity_factor

def calculate_time_in_seconds(df):
    time_in_seconds=[]
    for i in range(df.Tiempo.shape[0]):
        splits = df.Tiempo[i].split(':')
        time_in_sec= int(splits[0])*3600+int(splits[1])*60+int(splits[2].split(',')[0])
        time_in_seconds.append(time_in_sec)
    df['Seconds'] = time_in_seconds

def calculate_tss(df):
    df['TSS'] = (df['Seconds']*df['NP']*df['IF'])/(df['FTP']*3600)*100
    df.drop(['Tiempo'], inplace=True, axis=1)

def calculate_fatigue(df_old, df_actual):
    atl=[]
    count = 0
    yesterday_atl = 0
    if df_old.shape[0] > 0 :
        yesterday_atl = df_old['Fatigue'][df_old.shape[0]-1]
    for i in reversed(df_actual.index):
        if (count!=0):
            yesterday_atl = atl[count-1]
        current_atl = yesterday_atl*math.exp(-1/7) + df_actual.iloc[count].TSS * (1-math.exp(-1/7))
        atl.append(current_atl)
        count+=1
    df_actual['Fatigue'] = atl

def calculate_fitness(df_old, df_actual):
    ctl=[]
    count = 0
    yesterday_ctl = 0
    if df_old.shape[0] > 0 :
        yesterday_ctl = df_old['Fitness'][df_old.shape[0]-1]
    for i in reversed(df_actual.index):
        if (count!=0):
            yesterday_ctl = ctl[count-1]
        current_ctl = yesterday_ctl*math.exp(-1/42) + df_actual.iloc[count].TSS * (1-math.exp(-1/42))
        ctl.append(current_ctl)
        count+=1
    df_actual['Fitness'] = ctl

def calculate_freshness(df_actual):
    df_actual['Freshness'] = df_actual.Fitness - df_actual.Fatigue

def merge_rides_on_same_date(df_actual):
    df_actual.reset_index(drop=False, inplace=True)
    aggregation_functions = {'Fecha': 'first','NP':'mean', 'FTP': 'first', 'IF':'mean', 'Seconds':'sum', 'TSS':'sum', 'Fatigue':'mean','Fitness':'mean','Freshness':'mean'}
    df_new = df_actual.groupby(df_actual['Fecha']).aggregate(aggregation_functions)
    df_new['Fecha'] = df_new['Fecha'].apply(lambda x: x.strftime('%Y-%m-%d'))
    for i in range(df_new.shape[0]):
        df_new['Fecha'][i] = df_new['Fecha'][i].split(' ')[0]

    df_new.reset_index(drop=True, inplace=True)
    df_actual = df_new
    
def calculate_values(df_origin, df_actual):
    calculate_intensity_factor(df_actual)
    calculate_time_in_seconds(df_actual)
    calculate_tss(df_actual)
    calculate_fatigue(df_origin, df_actual)
    calculate_fitness(df_origin, df_actual)
    calculate_freshness(df_actual)
    merge_rides_on_same_date(df_actual)
    
def start_calculations(df_origin, df_dest):
    if df_dest.shape[0] > 0 :
        df_dates_between = get_between_dates(df_origin, df_dest)

        df_dest.set_index("Fecha", inplace = True)
        df_dates_between.set_index("Fecha", inplace = True)

        df_actual = merge_dfs(df_dest, df_dates_between)

        set_ftp(240, df_actual)
        calculate_values(df_origin, df_actual)

        df_actual.Fecha = df_actual.Fecha.astype(str)
        if df_origin.shape[0] > 0:
            df_origin = df_origin.append(df_actual, ignore_index = True)
        else:
            df_origin = df_actual

        df_origin.drop(['Unnamed: 0'], inplace=True, axis=1)
        