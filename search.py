import os
import re

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

# Initialize a dictionary to hold the results
results = {}

# Iterate over each file in the current directory
for filename in os.listdir('.'):
    if filename.endswith(".txt") and filename != "log.txt":
        # Extract the PID from the filename
        pid = re.search(r'\d+', filename).group()
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
        # Extract the process name from the content
        process_name_match = re.search(r'"([^"]+\.exe)"', content)
        process_name = process_name_match.group(1) if process_name_match else "Unknown"
        # Store the results in the dictionary
        results[pid] = (process_name, total_occurrences)

# Write the results to a new text file named results.txt
with open('results.txt', 'w') as log_file:
    for pid, (process_name, total_occurrences) in results.items():
        log_file.write(f"{pid} | {process_name} | {total_occurrences}\n")

# Print a success message
print("The search is complete. The results have been saved to results.txt.")
