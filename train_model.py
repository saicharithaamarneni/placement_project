import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

# TRAINING DATA

data = {

    "cgpa": [9,8,7,6,5,9,8,7],

    "projects": [3,2,2,1,0,4,3,1],

    "communication": [9,8,7,5,4,10,9,6],

    "internships": [2,1,1,0,0,2,2,1],

    "result": [1,1,1,0,0,1,1,0]
}
# DATAFRAME

df = pd.DataFrame(data)

# INPUTS

X = df.drop("result", axis=1)

# OUTPUT

y = df["result"]

# MODEL

model = RandomForestClassifier()

model.fit(X, y)

# SAVE MODEL

joblib.dump(model, "model.pkl")

print("Model Trained Successfully")