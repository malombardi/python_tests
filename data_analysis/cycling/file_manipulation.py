import pandas as pd
import os

def import_data(saved_data):
    df = pd.read_csv('../data/Activities.csv')
    df.drop(['Tipo de actividad', 'Favorito', 'Título', 'Distancia',
       'Calorías', 'Frecuencia cardiaca media',
       'Frecuencia cardiaca máxima', 'Velocidad media', 'Velocidad máxima',
       'Ganancia de altura', 'Altura perdida', 'Longitud media de zancada',
       'Relación vertical media', 'Oscilación vertical media',
       'Cadencia media de pedaleo', 'Cadencia de pedaleo máxima', 'Training Stress Score®',
       'Potencia media máxima (20 minutos)', 'Potencia media',
       'Potencia máxima', 'Dificultad', 'Fluidez', 'Brazadas totales',
       'Tiempo de ascenso', 'Duración de la inmersión', 'Temperatura mínima',
       'Intervalo en superficie', 'Descompresión', 'Mejor tiempo de vuelta',
       'Número de vueltas', 'Temperatura máxima'], inplace=True, axis=1)

    for i in range(df.shape[0]):
        df['Fecha'][i] = df['Fecha'][i].split(' ')[0]

    if saved_data.shape[0] > 0 :
        df = df[df['Fecha'] > saved_data['Fecha'][saved_data.shape[0]-1]]
    else:
        df = df[df['Fecha'] > '2020-10-11 ']

    for i in range(df.shape[0]):
        df['Fecha'][i] = df['Fecha'][i].split(' ')[0]

    df['Fecha']= pd.to_datetime(df['Fecha'])
    df = df.rename(columns={'Normalized Power® (NP®)':'NP'})
    df['NP']= pd.to_numeric(df['NP'])

    return df

def import_saved_data():
    try:
        return pd.read_csv('../data/saved.csv')
    except:
        return pd.DataFrame()
    

def save_df_to_csv(df):
    try:
        os.remove('../data/saved.csv')
    except:
        print("There is no old data")
    df.to_csv('../data/saved.csv')
    
def get_data_from_files():
    df_origin = import_saved_data()
    df_dest = import_data(df_origin)
    
    return df_origin, df_dest