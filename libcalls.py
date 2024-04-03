import subprocess

# Define a function to read PIDs from a file and execute ListDlls.exe for each PID
def execute_listdlls_for_pids(file_path):
    with open(file_path, 'r') as file:
        for pid in file:
            pid = pid.strip()  # Remove any leading/trailing whitespace
            if pid.isdigit():  # Check if the line is a valid PID
                command = f"ListDlls.exe {pid} > {pid}Dlls.txt"
                subprocess.run(command, shell=True)

# Call the function with the path to log.txt
execute_listdlls_for_pids("log.txt")
