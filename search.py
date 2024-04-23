import os
import re
import psutil
import csv

# Define the keywords to search for
keywords = [
    "BCRYPTPRIMITIVES.DLL",
    "CRYPT32.DLL",
    "CRYPTBASE.DLL",
    "CRYPTDLL.DLL",
    "CNGAUDIT.DLL",
    "RSAENH.DLL",
    "CRYPTSP.DLL"
]

# Function to get process name by PID
def get_process_name(pid):
    try:
        process = psutil.Process(int(pid))
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "Unknown"

# Read the existing CSV file and add a new column
csv_rows = []
if os.path.exists('int.csv'):
    with open('int.csv', mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            row["Number of crypto API calls"] = 0  # Initialize the new column with 0
            csv_rows.append(row)
        fieldnames = reader.fieldnames + ["Number of crypto API calls"]  # Add new column to fieldnames

# Iterate over each file in the current directory
for filename in os.listdir('.'):
    if filename.endswith(".txt") and filename != "log.txt":
        # Extract the PID from the filename
        pid_match = re.search(r'\d+', filename)
        if pid_match:
            pid = pid_match.group()
            # Initialize the count for each keyword
            keyword_counts = {keyword: 0 for keyword in keywords}
            # Open the file and read its contents
            with open(filename, 'r') as file:
                content = file.read().lower()  # Convert content to lowercase
                # Search for each keyword and count its occurrences
                for keyword in keywords:
                    keyword_lower = keyword.lower()  # Convert keyword to lowercase
                    keyword_counts[keyword] = content.count(keyword_lower)
            # Calculate the total occurrences of all keywords
            total_occurrences = sum(keyword_counts.values())
            # Update the corresponding row in csv_rows
            for row in csv_rows:
                if row["pid"] == pid:
                    row["Number of crypto API calls"] = total_occurrences

# Write the updated data back to int.csv
with open('int.csv', mode='w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(csv_rows)

# Print a success message
print("The CSV has been updated with the number of crypto API calls.")
subprocess.run(['python', 'sequential.py'])
