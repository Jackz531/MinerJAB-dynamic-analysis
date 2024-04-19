import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Load the model from the job file
clf_loaded = joblib.load('random_forest.joblib')

# Load your test data
test_data = pd.read_csv('test_data.csv')

# Encode the 'Cryptojacker or not' column to numerical values
# This assumes that 'yes' is encoded as 1 and 'no' as 0
label_encoder = LabelEncoder()
test_data['Cryptojacker or not'] = label_encoder.fit_transform(test_data['Cryptojacker or not'])

# Prepare the data for testing
X_test = test_data[['median_cpu_percent','quadratic_deviation','ram_usage','upload_speed','median_network_rate','download_speed','Number of crypto API calls']]
PIDs = test_data['pid']

# Make predictions on the test data
predictions = clf_loaded.predict(X_test)

# Add predictions to the test data
test_data['Predicted'] = label_encoder.inverse_transform(predictions)  # Convert numerical predictions back to 'yes'/'no'

# Calculate performance metrics
accuracy = accuracy_score(test_data['Cryptojacker or not'], predictions)
recall = recall_score(test_data['Cryptojacker or not'], predictions)
f1 = f1_score(test_data['Cryptojacker or not'], predictions)
conf_matrix = confusion_matrix(test_data['Cryptojacker or not'], predictions)

for pid, prediction in zip(PIDs, test_data['Predicted']):
    print(f'PID: {pid}, Predicted Label: {prediction}')
    
# Print the performance metrics
print(f'Accuracy: {accuracy}')
print(f'Recall: {recall}')
print(f'F1 Score: {f1}')
print(f'Confusion Matrix:\n{conf_matrix}')

# Save the test data with predictions to a new CSV file
test_data.to_csv('test_data_with_predictions.csv', index=False)
import subprocess

subprocess.run(['python', 'terminate.py'])
