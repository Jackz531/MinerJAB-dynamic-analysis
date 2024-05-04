import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder

# Load the model from the job file
clf_loaded = joblib.load('random_forest.joblib')

# Load your test data
test_data = pd.read_csv('int.csv')

# Prepare the data for testing (use only desired features)
X_test = test_data[['median_cpu_percent', 'quadratic_deviation', 'ram_usage', 'median_network_rate','Number of crypto API calls']]
PIDs = test_data['pid']

# Make predictions on the test data
predictions = clf_loaded.predict(X_test)

# Add predictions to the test data
# Assuming 'yes' is encoded as 1 and 'no' as 0 after fitting the LabelEncoder
test_data['Predicted'] = predictions

# Filter rows with predicted Cryptojackers (assuming 'yes' is encoded as 1)
cryptojacker_rows = test_data[test_data['Predicted'] == 1]

# Save the filtered rows (PIDs with Cryptojackers) to the CSV file
cryptojacker_rows.to_csv('int.csv', index=False)
