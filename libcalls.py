import subprocess
import pandas as pd
import os

# Read the existing int.csv file
df = pd.read_csv("int.csv")

# Read the PIDs from log.txt and store them in a set
valid_pids = set()
with open("log.txt", "r") as log_file:
    for line in log_file:
        pid = line.strip()
        if pid.isdigit():
            valid_pids.add(int(pid))  # Convert to integer

# Filter rows based on valid PIDs
df_filtered = df[df['pid'].isin(valid_pids)]

# Execute ListDlls.exe for each valid PID and redirect output to a text file
for pid in valid_pids:
    command = f"ListDlls.exe {pid} > {pid}Dlls.txt"
    subprocess.run(command, shell=True)

# Write the filtered rows back to int.csv
df_filtered.to_csv("int.csv", index=False)

print("Filtered int.csv based on log.txt and executed ListDlls for each PID.")


subprocess.run(['python', 'search.py'])
