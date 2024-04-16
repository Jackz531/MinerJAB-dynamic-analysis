import os
import re
import psutil

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

# Check if results.txt exists, if not, create it and write the header
if not os.path.exists('results.txt'):
    with open('results.txt', 'w') as log_file:
        log_file.write("PID\t\tPname\t\tNumber of calls\n")

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
            # Get the process name using the PID
            process_name = get_process_name(pid)
            # Append the results to results.txt
            with open('results.txt', 'a') as log_file:
                log_file.write(f"{pid}\t{process_name}\t{total_occurrences}\n")

# Print a success message
print("The search is complete. The results have been saved to results.txt.")
