import io
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from django.forms import forms
from tensorflow.python import debug as tf_debug

logger = logging.getLogger('django')


class NeuralNetworkForm(forms.Form):

    @staticmethod
    def get_price_linear_regression_plot():
        x_time = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float64)
        y_price = np.array([1000, 1150, 1200, 1375, 1425, 1500, 1700, 1715, 1800, 1900], dtype=np.float64)

        fig = plt.figure(1, figsize=(9, 4))
        plt.subplot(111)
        plt.xlabel('minute')
        plt.ylabel('Price')
        plt.title("Linear regression by learning rate")
        plt.plot(x_time, y_price, '*', label='Real data (ETH price)')

        learning_rates = [
            {"rate": 0.000001, "plot": "--r"},
            {"rate": 0.00001, "plot": "--g"},
            {"rate": 0.0001, "plot": "--y"},
            {"rate": 0.001, "plot": "--o"},
            {"rate": 0.0025, "plot": "--p"},
        ]

        for learning_rate in learning_rates:
            NeuralNetworkForm.__add_linear_plot(x_time, y_price, learning_rate)
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        return buf

    @staticmethod
    def __add_linear_plot(x_time, y_price, learning_rate):
        error = 0
        np.array(x_time, dtype=np.float64)

        m = tf.Variable(0.39)
        b = tf.Variable(0.2)

        for x, y in zip(x_time, y_price):
            y_hat = m * x + b
            error += (y - y_hat) ** 2
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate["rate"])
        train = optimizer.minimize(error)
        init = tf.global_variables_initializer()
        session = tf.Session()
        # session = tf_debug.TensorBoardDebugWrapperSession(session, "Kamil:3003")
        with session as sess:
            sess.run(init)
            epochs = 100
            for i in range(epochs):
                sess.run(train)
            final_slope, final_intercept = sess.run([m, b])

        y_pred_plot = final_slope * x_time + final_intercept
        plt.plot(x_time, y_pred_plot, learning_rate["plot"], label='Learning rate {}'.format(learning_rate["rate"]))

    @staticmethod
    def get_regression_for_million_samples_example():
        # 1 Million Points
        x_data = np.linspace(0.0, 10.0, 1000000)
        noise = np.random.randn(len(x_data))

        # y = mx + b + noise_levels
        b = 5

        y_true = (0.5 * x_data) + 5 + noise

        my_data = pd.concat([pd.DataFrame(data=x_data, columns=['X Data']),
                             pd.DataFrame(data=y_true, columns=['Y'])],
                            axis=1)

        batch_size = 8

        m = tf.Variable(0.5)
        b = tf.Variable(1.0)

        xph = tf.placeholder(tf.float32, [batch_size])
        yph = tf.placeholder(tf.float32, [batch_size])

        y_model = m * xph + b

        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        error = tf.reduce_sum(tf.square(yph - y_model))
        train = optimizer.minimize(error)

        init = tf.global_variables_initializer()

        with tf.Session() as sess:
            sess.run(init)
            batches = 1000
            for i in range(batches):
                rand_ind = np.random.randint(len(x_data), size=batch_size)
                feed = {xph: x_data[rand_ind], yph: y_true[rand_ind]}
                sess.run(train, feed_dict=feed)
            model_m, model_b = sess.run([m, b])

        y_hat = x_data * model_m + model_b

        fig = plt.figure(1, figsize=(9, 4))
        plt.subplot(111)
        plt.xlabel('X Data')
        plt.ylabel('Y Data')
        plt.title("Linear regression from million points")
        data = my_data.sample(n=250)

        plt.plot(x_data, y_hat, 'r')
        plt.plot(data['X Data'], data['Y'], '*')

        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        return buf
