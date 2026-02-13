from sklearn.linear_model import LinearRegression
import numpy as np

def forecast(history):
    if len(history) < 2:
        return 0

    X = np.arange(len(history)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, history)

    return int(model.predict([[len(history) + 1]])[0])
