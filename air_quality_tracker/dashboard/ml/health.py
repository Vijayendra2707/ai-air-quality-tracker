from sklearn.ensemble import RandomForestClassifier

# Sample training data
X = [
    [30, 50, 25, 0, 0],   # good air, young, no issues
    [80, 60, 35, 0, 0],
    [120, 65, 40, 1, 0],
    [180, 70, 60, 1, 0],
    [220, 75, 65, 1, 1],
    [300, 85, 75, 1, 1]
]

y = ["Low", "Low", "Moderate", "Moderate", "Severe", "Severe"]

model = RandomForestClassifier()
model.fit(X, y)


def predict_health(data):
    return model.predict([data])[0]
