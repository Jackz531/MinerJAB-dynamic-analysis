import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from sklearn import tree
import matplotlib.pyplot as plt

# Load your training data from a CSV file
train_data = pd.read_csv('train_data3.csv')

# Encode the 'Cryptojacker or not' column to numerical values
label_encoder = LabelEncoder()
train_data['Cryptojacker or not'] = label_encoder.fit_transform(train_data['Cryptojacker or not'])

# Prepare the data for training
# Ensure the column names match the ones in your CSV file
X_train = train_data.drop(['pid', 'Cryptojacker or not'], axis=1)
y_train = train_data['Cryptojacker or not']

# Initialize the Random Forest Classifier
clf = RandomForestClassifier(n_estimators=50, max_depth=5, min_samples_split=5, min_samples_leaf=2, random_state=42)

# Train the classifier
clf.fit(X_train, y_train)

# Save the trained model as a job file
joblib.dump(clf, 'random_forest.joblib')
