import pandas as pd

# Load the CSV file into a DataFrame
df = pd.read_csv('malware.csv')

# Define the thresholds
c0 = 30  # Threshold for CPU usage
r0 = 450  # Lower bound for RAM usage
r1 = 2500  # Upper bound for RAM usage
n0 = 500  # Threshold for network transfer rate
crypto_api_calls_threshold = 2  # Threshold for number of crypto API calls
q0=10 # Threshold for quadratic deviation
# Define a function to write the result to a file
def write_result(file, pid, is_malware):
    status = "is classified as malware." if is_malware else "is not a malware."
    file.write(f"PID: {pid} {status}\n")

# Open a file to write the results
with open('results.txt', 'w') as file:
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Check the conditions for each PID
        if row['median_cpu_percent'] > c0:
            if row['median_network_rate'] > n0:
                if row['quadratic_deviation'] > q0:
                    if row['Number of crypto API calls'] > crypto_api_calls_threshold:
                        if r0 <= row['ram_usage'] <= r1:
                            # If all conditions are met, call the function to write the result
                            write_result(file, row['pid'], True)
                        else:
                            # If any condition fails, call the function to write the result
                            write_result(file, row['pid'], False)
                            continue
                    else:
                        write_result(file, row['pid'], False)
                        continue
                else:
                    write_result(file, row['pid'], False)
                    continue
            else:
                write_result(file, row['pid'], False)
                continue
        else:
            write_result(file, row['pid'], False)
            continue

# Display a message indicating the analysis is complete
print("Sequential analysis complete")
