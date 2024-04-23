import pandas as pd
import psutil
import os

# Function to get the executable path from a PID
def get_executable_path(pid):
    for proc in psutil.process_iter():
        if proc.pid == pid:
            return proc.exe()
    return None

# Function to terminate the process by PID
def terminate_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Process with PID {pid} terminated successfully.")
    except psutil.NoSuchProcess:
        print(f"No process found for PID {pid}")

# Function to delete the executable file
def delete_executable(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Executable file {file_path} deleted successfully.")
    else:
        print(f"Executable file {file_path} does not exist.")

# Function to process the CSV, terminate processes, and delete executables
def process_csv_terminate_delete(csv_file_path):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Iterate over the rows in the DataFrame
    for index, row in df.iterrows():
        pid = row['pid']
        executable_path = get_executable_path(pid)
        if executable_path:
            terminate_process(pid)
            delete_executable(executable_path)
        else:
            print(f"No executable found for PID {pid}")

# Example usage
csv_file_path = 'int.csv'  # Replace with the actual path to your CSV file
process_csv_terminate_delete(csv_file_path)
