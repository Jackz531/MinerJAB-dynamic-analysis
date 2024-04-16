import pandas as pd
import os
import signal

# Load the test data with predictions
test_data = pd.read_csv('test_data_with_predictions.csv')

# Iterate over the rows in the DataFrame
for index, row in test_data.iterrows():
    # Check if the process is labeled as a cryptojacker
    if row['Predicted'] == 'yes':
        pid = row['PID']
        try:
            # Terminate the process
            os.kill(pid, signal.SIGTERM)
            print(f"Process with PID {pid} has been terminated.")
        except Exception as e:
            print(f"Could not terminate process with PID {pid}. Reason: {e}")


