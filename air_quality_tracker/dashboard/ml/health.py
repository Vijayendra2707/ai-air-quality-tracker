from sklearn.ensemble import RandomForestClassifier

def predict_health(data):
    X = [
        [50,60,25,0,0],
        [180,70,60,1,0],
        [250,80,70,1,1]
    ]
    y = ["Low","Moderate","Severe"]

    model = RandomForestClassifier()
    model.fit(X, y)

    return model.predict([data])[0]
