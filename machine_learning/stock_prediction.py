from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
rcParams['figure.figsize']=20,10
import yfinance as yf
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM,Dropout,Dense

pd.options.mode.chained_assignment = None 
BTC_USD = yf.Ticker("BTC-USD")
btc_hist = BTC_USD.history(period = "max")

plt.figure(figsize=(16,8))
plt.plot(btc_hist["Close"],label = 'Close Price history')

data=btc_hist.sort_index(ascending = True, axis = 0)
new_dataset=pd.DataFrame(index = range(0, len(btc_hist)), columns = ['Date','Close'])

for i in range(0,len(data)):
    new_dataset["Date"][i] = data.index[i]
    new_dataset["Close"][i] = data["Close"][i]
    
new_dataset.index = new_dataset.Date
new_dataset.drop("Date", axis = 1, inplace = True)

scaler = MinMaxScaler(feature_range = (0, 1))
final_dataset = new_dataset.values

data_size_75 = int(final_dataset.shape[0] * 0.75)

train_data = final_dataset[0:data_size_75,:]
valid_data = final_dataset[data_size_75:,:]

scaled_data = scaler.fit_transform(final_dataset)

x_train_data, y_train_data = [],[]

for i in range(60, len(train_data)):
    x_train_data.append(scaled_data[i-60:i,0])
    y_train_data.append(scaled_data[i,0])
    
x_train_data, y_train_data = np.array(x_train_data), np.array(y_train_data)

x_train_data = np.reshape(x_train_data, (x_train_data.shape[0], x_train_data.shape[1], 1))

lstm_model = tf.keras.Sequential()
lstm_model.add(layers.LSTM(units = 50, return_sequences = True, input_shape = (x_train_data.shape[1],1)))
lstm_model.add(layers.LSTM(units = 50))
lstm_model.add(layers.Dense(1))

inputs_data = new_dataset[len(new_dataset)-len(valid_data)-60:].values
inputs_data = inputs_data.reshape(-1, 1)
inputs_data = scaler.transform(inputs_data)

lstm_model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(0.01))
lstm_model.fit(x_train_data, y_train_data, epochs = 1, batch_size = 1, verbose = 2)

X_test = []
for i in range(60, inputs_data.shape[0]):
    X_test.append(inputs_data[i-60:i,0])
X_test = np.array(X_test)

X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
predicted_closing_price = lstm_model.predict(X_test)
predicted_closing_price = scaler.inverse_transform(predicted_closing_price)

train_data = new_dataset[:data_size_75]
valid_data = new_dataset[data_size_75:]
valid_data['Predictions'] = predicted_closing_price
plt.figure(figsize=(16,8))
plt.plot(train_data['Close'])
plt.plot(valid_data[['Close', 'Predictions']])
plt.show()
