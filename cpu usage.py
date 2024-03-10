import psutil
import os
import time

def get_cpu_percent_per_core(process):
    # Get the number of CPU cores
    num_cores = psutil.cpu_count(logical=True)
    # Calculate the CPU utilization per core
    return process.cpu_percent() / num_cores

def get_all_processes():
    # Retrieve all processes with their CPU and memory usage
    processes = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            cpu_percent_per_core = get_cpu_percent_per_core(process)
            if cpu_percent_per_core >= 10:  # Filter processes with CPU usage above 10 percent per core
                processes.append({
                    'pid': process.pid,
                    'name': process.name(),
                    'cpu_percent': cpu_percent_per_core,
                    'memory_percent': process.memory_percent(),
                    # Removed the 'network_io' key as it's not supported per process
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


def display_processes(processes):
    # Display the processes in a formatted table
    print(f"{'PID':<6} {'Name':<25} {'CPU%':>5} {'Memory%':>8}")
    print("-" * 50)
    for process in processes:
        # Print process details without network I/O
        print(f"{process['pid']:<6} {process['name']:<25} {process['cpu_percent']:>5} {process['memory_percent']:>8.2f}")

def terminate_process(pid):
    # Terminate a process by PID
    try:
        p = psutil.Process(pid)
        p.terminate()
        print(f"Process {pid} terminated.")
    except psutil.NoSuchProcess:
        print(f"No process found with PID: {pid}")
    except psutil.AccessDenied:
        print(f"Access denied to terminate process with PID: {pid}")

def get_network_utilization():
    # Get network I/O statistics
    net_io = psutil.net_io_counters()
    return f"Bytes Sent: {net_io.bytes_sent}, Bytes Recv: {net_io.bytes_recv}"

if __name__ == "__main__":
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console window
            print("Mini Task Manager")
            print(get_network_utilization())  # Display network utilization
            print("-" * 65)
            processes = get_all_processes()
            display_processes(processes)
            
            print("\nOptions:")
            print("1. Refresh process list")
            print("2. Terminate a process")
            print("3. Exit")
            choice = input("Enter your choice: ")
            
            if choice == '1':
                continue
            elif choice == '2':
                pid_to_terminate = int(input("Enter the PID of the process to terminate: "))
                terminate_process(pid_to_terminate)
                time.sleep(2)  # Wait for 2 seconds before refreshing
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")
                time.sleep(2)  # Wait for 2 seconds before refreshing
    except KeyboardInterrupt:
        print("Mini Task Manager stopped.")


