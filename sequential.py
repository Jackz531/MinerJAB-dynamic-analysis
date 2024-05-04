import pandas as pd
import subprocess
# Load the CSV file into a DataFrame
df = pd.read_csv('goodware.csv')
# Define the thresholds
c0 = 10  # Threshold for CPU usage
r0 = 278  # Lower bound for RAM usage
r1 = 2400  # Upper bound for RAM usage
n0 = 55  # Threshold for network transfer rate
crypto_api_calls_threshold = 2  # Threshold for number of crypto API calls
q0 = 10.5  # Threshold for quadratic deviation
# Define a function to check if a row is classified as malware
def is_malware(row):
    return (row['median_cpu_percent'] >=c0 and
            row['median_network_rate'] >=n0 and
            row['quadratic_deviation'] >=q0 and
            row['Number of crypto API calls'] >=crypto_api_calls_threshold and
            r0 <= row['ram_usage'] <= r1)
# Apply the function to classify each row and filter the DataFrame
malware_df = df[df.apply(is_malware, axis=1)]
# Save the filtered DataFrame to a new CSV file
malware_df.to_csv('int.csv', index=False)
print("Sequential analysis complete. Only malware rows have been kept in int.csv.")
subprocess.run(['python', 'terminate.py'])
