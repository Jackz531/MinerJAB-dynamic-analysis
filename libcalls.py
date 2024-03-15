import subprocess

# Ask for input PID
pid = input("Enter PID: ")

# Execute "ListDlls.exe [PID] > [PID]Dlls.txt" in command line
command = f"ListDlls.exe {pid} > {pid}Dlls.txt"
subprocess.run(command, shell=True)