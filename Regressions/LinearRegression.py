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


import tensorflow.compat.v2.feature_column as fc

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



for item in RegressionDict_bbg.keys():
    print(item)
    x = AllPrices[RegressionDict_bbg[item]['x']]
    y = AllPrices[RegressionDict_bbg[item]['x']]
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




dftrain = pd.read_csv('https://storage.googleapis.com/tf-datasets/titanic/train.csv')
dfeval = pd.read_csv('https://storage.googleapis.com/tf-datasets/titanic/eval.csv')
y_train = dftrain.pop('survived')
y_eval = dfeval.pop('survived')