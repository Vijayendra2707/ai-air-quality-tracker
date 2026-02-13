from sklearn.ensemble import IsolationForest

def detect(history):
    if len(history) < 5:
        return []

    model = IsolationForest(contamination=0.1)
    model.fit([[x] for x in history])

    return model.predict([[x] for x in history])
