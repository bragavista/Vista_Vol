try:
    import Util
    from Util import BloombergAPI_new as BloombergAPI
    from Util import QuantMetrics as QuantMetrics
    from Util import EmailSender as EmailSender
    from FetchData import EQ_FetchHistoricalPrices
    print('try worked')

except:
    import Util.BloombergAPI_new as BloombergAPI
    import Util.QuantMetrics as QuantMetrics
    import Util.EmailSender as EmailSender
    import FetchData.EQ_FetchHistoricalPrices as EQ_FetchHistoricalPrices


class LinearRegression():
    ''' Class that implemnets Simple Linear Regression '''

    def __init__(self):
        self.b0 = 0
        self.b1 = 0

    def fit(self, X, y):
        mean_x = np.mean(X)
        mean_y = np.mean(y)

        SSxy = np.sum(np.multiply(X, y)) - len(x) * mean_x * mean_y
        SSxx = np.sum(np.multiply(X, x)) - len(x) * mean_x * mean_x

        self.b1 = SSxy / SSxx
        self.b0 = mean_y - self.b1 * mean_x

    def predict(self, input_data):
        return self.b0 + self.b1 * input_data

import matplotlib.pyplot as plt

import tensorflow.compat.v2.feature_column as fc

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import tensorflow as tf

import numpy as np
import pandas as pd
StartDate = 20200618
EndDate = 20200718
y = "VIX Index"
x = "SPX Index"

RegressionDict_bbg = {  'vix_spx' :
                                {'y' : "VIX Index", 'x' : "SPX Index"},
                    'credit_hy_SPX':
                                {'y' : "CDX HY CDSI GEN 5Y PRC Index", 'x' : "SPX Index"},
                    'credit_ig_SPX':
                                {'y' : "CDX IG CDSI GEN 5Y SPRD Index", 'x' : "SPX Index"},
                    'vix_credit_hy':
                                {'y' : "VIX Index", 'x' : "CDX HY CDSI GEN 5Y PRC Index"}
                    }

all_assets = list()
for item in RegressionDict_bbg.keys():
    print(item)
    for subitem in RegressionDict_bbg[item]:
        all_assets.append(RegressionDict_bbg[item][subitem])

all_assets = list(np.unique(all_assets))
AllPrices = EQ_FetchHistoricalPrices.pull_price_history(all_assets,StartDate=StartDate,EndDate=EndDate)
AllPrices.columns = [element[0] for element in AllPrices.columns]


for item in RegressionDict_bbg.keys():
    print(item)
    x = AllPrices[RegressionDict_bbg[item]['x']].array
    y = AllPrices[RegressionDict_bbg[item]['y']].array
    n = len(x)

    X = tf.placeholder("float")
    Y = tf.placeholder("float")

    W = tf.Variable(np.random.randn(), name = "W")
    b = tf.Variable(np.random.randn(), name = "b")
    learning_rate = 0.01
    training_epochs = 1000
    # Hypothesis
    y_pred = tf.add(tf.multiply(X, W), b)

    # Mean Squared Error Cost Function
    cost = tf.reduce_sum(tf.pow(y_pred - Y, 2)) / (2 * n)

    # Gradient Descent Optimizer
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    # Global Variables Initializer
    init = tf.global_variables_initializer()

    with tf.Session() as sess:

        # Initializing the Variables
        sess.run(init)

        # Iterating through all the epochs
        for epoch in range(training_epochs):

            # Feeding each data point into the optimizer using Feed Dictionary
            for (_x, _y) in zip(x, y):
                sess.run(optimizer, feed_dict={X: _x, Y: _y})

                # Displaying the result after every 50 epochs
            if (epoch + 1) % 50 == 0:
                # Calculating the cost a every epoch
                c = sess.run(cost, feed_dict={X: x, Y: y})
                print("Epoch", (epoch + 1), ": cost =", c, "W =", sess.run(W), "b =", sess.run(b))

                # Storing necessary values to be used outside the Session
        training_cost = sess.run(cost, feed_dict={X: x, Y: y})
        weight = sess.run(W)
        bias = sess.run(b)

        predictions = weight * x + bias





model = LinearRegression()
model.fit(x, y)
predictions = model.predict(x)
plt.scatter(x = x, y = y, color='orange')
plt.plot(predictions, color='orange')
plt.show()