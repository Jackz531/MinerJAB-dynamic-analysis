import os
import time
import psutil
import math

def get_cpu_percent_per_core(process, interval=0.1):
    # Get the number of CPU cores
    num_cores = psutil.cpu_count(logical=True)
    # Calculate the CPU utilization per core
    return process.cpu_percent(interval=interval) / num_cores

def get_all_processes(cpu_threshold, ram_threshold, cpu_usage_history):
    # Retrieve all processes with their CPU and memory usage
    processes = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            cpu_percent_per_core = get_cpu_percent_per_core(process)
            memory_usage_mb = process.memory_info().rss / (1024 * 1024)  # Convert memory usage to MB
            if cpu_percent_per_core >= cpu_threshold and memory_usage_mb >= ram_threshold:  # Filter processes based on user-defined thresholds
                # Update the CPU usage history for the process
                if process.pid not in cpu_usage_history:
                    cpu_usage_history[process.pid] = []
                cpu_usage_history[process.pid].append(cpu_percent_per_core)
                # Calculate the quadratic standard deviation for CPU usage
                qsd_cpu_usage = quadratic_standard_deviation(cpu_usage_history[process.pid])
                processes.append({
                    'pid': process.pid,
                    'name': process.name(),
                    'cpu_percent': cpu_percent_per_core,
                    'memory_usage_mb': memory_usage_mb,
                    'qsd_cpu_usage': qsd_cpu_usage  # Add the quadratic standard deviation attribute
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def quadratic_standard_deviation(cpu_usages):
    mean_of_squares = sum([usage**2 for usage in cpu_usages]) / len(cpu_usages)
    return math.sqrt(mean_of_squares)

def display_processes(processes):
    # Display the processes in a formatted table
    print(f"{'PID':<6} {'Name':<25} {'CPU%':>5} {'RAM MB':>8} {'QSD':>5}")
    print("-" * 65)
    for process in processes:
        # Print process details including the quadratic standard deviation
        print(f"{process['pid']:<6} {process['name']:<25} {process['cpu_percent']:>5.2f} {process['memory_usage_mb']:>8.2f} {process['qsd_cpu_usage']:>5.2f}")

def get_network_utilization():
    # Get network I/O statistics
    net_io = psutil.net_io_counters()
    return f"Bytes Sent: {net_io.bytes_sent}, Bytes Recv: {net_io.bytes_recv}"

if __name__ == "__main__":
    cpu_threshold = float(input("Enter the CPU usage threshold (in %): "))
    ram_threshold = float(input("Enter the RAM usage threshold (in MB): "))
    refresh_interval = float(input("Enter the refresh interval (in seconds): "))
    cpu_usage_history = {}  # Dictionary to keep track of CPU usage history for each process
    
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console window
            print("Mini Task Manager - Monitoring Mode")
            print(get_network_utilization())  # Display network utilization
            print("-" * 65)
            processes = get_all_processes(cpu_threshold, ram_threshold, cpu_usage_history)
            display_processes(processes)
            time.sleep(refresh_interval)  # Wait for the specified interval before refreshing
    except KeyboardInterrupt:
        print("Dynamic Analaysis stopped.")
