import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Load the model from the job file
clf_loaded = joblib.load('random_forest.joblib')

# Load your test data
test_data = pd.read_csv('test_data.csv')

# Encode the 'Crytpojacker or not' column to numerical values
# This assumes that 'yes' is encoded as 1 and 'no' as 0
label_encoder = LabelEncoder()
test_data['Crytpojacker or not'] = label_encoder.fit_transform(test_data['Crytpojacker or not'])

# Prepare the data for testing
X_test = test_data[['CPU utilization', 'CPU Quadtric deviation', 'Ram Usage', 'Network Upload Rate', 'Number of crypto api calls']]
PIDs = test_data['PID']

# Make predictions on the test data
predictions = clf_loaded.predict(X_test)

# Add predictions to the test data
test_data['Predicted'] = label_encoder.inverse_transform(predictions)  # Convert numerical predictions back to 'yes'/'no'

# Calculate performance metrics
accuracy = accuracy_score(test_data['Crytpojacker or not'], predictions)
recall = recall_score(test_data['Crytpojacker or not'], predictions)
f1 = f1_score(test_data['Crytpojacker or not'], predictions)
conf_matrix = confusion_matrix(test_data['Crytpojacker or not'], predictions)

for pid, prediction in zip(PIDs, test_data['Predicted']):
    print(f'PID: {pid}, Predicted Label: {prediction}')
    
# Print the performance metrics
print(f'Accuracy: {accuracy}')
print(f'Recall: {recall}')
print(f'F1 Score: {f1}')
print(f'Confusion Matrix:\n{conf_matrix}')

# Save the test data with predictions to a new CSV file
test_data.to_csv('test_data_with_predictions.csv', index=False)

# Function to terminate the process based on PID

