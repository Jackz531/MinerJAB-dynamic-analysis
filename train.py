import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load your training data from a CSV file
train_data = pd.read_csv('train_data.csv')

# Encode the 'Crytpojacker or not' column to numerical values
label_encoder = LabelEncoder()
train_data['Crytpojacker or not'] = label_encoder.fit_transform(train_data['Crytpojacker or not'])

# Prepare the data for training
X_train = train_data.drop(['PID', 'Crytpojacker or not'], axis=1)
y_train = train_data['Crytpojacker or not']

# Initialize the Random Forest Classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the classifier
clf.fit(X_train, y_train)

# Save the trained model as a job file
joblib.dump(clf, 'random_forest.joblib')
