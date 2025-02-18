# -*- coding: utf-8 -*-
"""cnn.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-J-gmfF8lY-j4NpvOpsec27AwxoRFUAq
"""

# Commented out IPython magic to ensure Python compatibility.
from numpy import array
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
import math
import numpy as np
from sklearn.metrics import mean_squared_error
import pandas as pd
import matplotlib.pylab as plt
# %matplotlib inline
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 15, 6
rcParams['axes.titlesize'] = 'xx-large'
rcParams['axes.titleweight'] = 'bold'
rcParams["legend.loc"] = 'upper left'

# Take in dataset and graph for reference
dateparse = lambda dates: pd.datetime.strptime(dates, '%Y-%m-%d')
data = pd.read_csv('http://kdl.cs.umb.edu/CS670/data/Ganges_1996_2016.csv', parse_dates=['Date'], index_col='Date',date_parser=dateparse)
data = data.astype('float64')

data.fillna(method='ffill', inplace=True)
plt.plot(data)

# Split data sets
def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the sequence
		if end_ix > len(sequence)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequence.iloc[i:end_ix].values, sequence.iloc[end_ix].values
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)

# Split data sets and check shape
n_steps = 20
X, y = split_sequence(data, n_steps)
  
# Split into test, validation, and training
#train_split = 5094
train_split = 5010
#valid_split = 5824
valid_split = 5740

X_train, y_train = X[:train_split],y[:train_split]
X_valid, y_valid = X[train_split:valid_split],y[train_split:valid_split]
X_test, y_test = X[valid_split:],y[valid_split:]

from keras.layers import Dropout
cnn = Sequential()
cnn.add(Conv1D(filters = 64,kernel_size = 2, activation = 'relu',input_shape = (n_steps,1)))
#cnn.add(MaxPooling1D(pool_size=2))
cnn.add(Flatten())
cnn.add(Dense(35,activation='relu'))
cnn.add(Dropout(0.1))
cnn.add(Dense(1))
cnn.compile(optimizer='adam',loss='mse')
cnn.summary()

history = cnn.fit(X_train, y_train, validation_data = (X_valid, y_valid), epochs=50, verbose=1)

# Task 2 Plot LSTM for original Data
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model train vs validation loss for original Data')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper right')
plt.show()

# make predictions
predict = cnn.predict(X_test)
# calculate root mean squared error
testScore = math.sqrt(mean_squared_error(y_test, predict))
print('Test Score CNN: %.2f RMSE' % (testScore))

# Show predictions vs ground truth values for CNN
predict_plot = pd.DataFrame(predict, data.index[valid_split+n_steps:])
plt.plot(data)
plt.plot(predict_plot)
plt.show()

periods = 5
ts_dif = data - data.shift(periods=periods)
#ts_dif.dropna(inplace=True)
ts_dif.fillna(method='ffill', inplace=True)

# Split data sets and check shape
n_steps = 20
X_dif, y_dif = split_sequence(ts_dif, n_steps)
  
# Split into test, validation, and training
train_split_dif = 5015 - periods
valid_split_dif = 5745 - periods
X_train_dif, y_train_dif = X_dif[:train_split_dif],y_dif[:train_split_dif]
X_valid_dif, y_valid_dif = X_dif[train_split_dif:valid_split_dif],y_dif[train_split_dif:valid_split_dif]
X_test_dif, y_test_dif = X_dif[valid_split_dif:],y_dif[valid_split_dif:]

cnn_dif = Sequential()
cnn_dif.add(Conv1D(filters = 64,kernel_size = 2, activation = 'relu',input_shape = (n_steps,1)))
cnn_dif.add(MaxPooling1D(pool_size=2))
cnn_dif.add(Flatten())
cnn_dif.add(Dense(15,activation='relu'))
cnn_dif.add(Dropout(0.1))
cnn_dif.add(Dense(1))
cnn_dif.compile(optimizer='adam',loss='mse')
cnn_dif.summary()
cnn_dif.fit(X_train, y_train, validation_data = (X_valid, y_valid), epochs=90, verbose=1)

predict_dif = cnn_dif.predict(X_test_dif)

# invert differenced value
def inverse_diff(pred, periods):
  prediction = []
  vs = valid_split
  for i in range(len(pred)):
    hist = data.values[:vs]
    p = pred[i] + hist[-periods]
    prediction.append(p)
    vs = vs+1
  return prediction
#inverse differnce predictions and plot
history_r = [x for x in data.values][:valid_split]


predict_invdif = inverse_diff(predict_dif, periods)

# calculate root mean squared error
testScore_dif = math.sqrt(mean_squared_error(y_test, predict_invdif))
print('Test Score CNN: %.2f RMSE' % (testScore_dif))

# Show predictions vs ground truth values for CNN
predict_plot2 = pd.DataFrame(predict_invdif, data.index[valid_split+n_steps:])
plt.plot(data)
plt.plot(predict_plot2)
plt.show()