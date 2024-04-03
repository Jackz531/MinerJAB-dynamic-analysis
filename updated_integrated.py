from scapy.all import *
import psutil
from collections import defaultdict
import os
from threading import Thread
import pandas as pd
from datetime import datetime
import time
import math
import numpy as np
import warnings



# Filter out the specific RuntimeWarning
warnings.filterwarnings("ignore", message="Mean of empty slice", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="invalid value encountered in scalar divide", category=RuntimeWarning)
# Get all network adapter's MAC addresses
all_macs = {iface.mac for iface in ifaces.values()}

# A dictionary to map each connection to its corresponding process ID (PID)
connection2pid = {}

# A dictionary to map each process ID (PID) to total Upload (0) and Download (1) traffic
pid2traffic = defaultdict(lambda: [0, 0])

# A dictionary to map each process ID (PID) to the sum of CPU usage
pid2cpu_usage_sum = defaultdict(int)
# A dictionary to map each process ID (PID) to the sum of squares of CPU usage
pid2cpu_usage_squaresum = defaultdict(int)
pid2cpu_usage_values = defaultdict(list)
pid2upload_speed_values = defaultdict(list)

pid2count = defaultdict(int)

# The global Pandas DataFrame that's used to track previous traffic stats
global_df = None

# Global boolean for program status
is_program_running = True

# User-defined thresholds
cpu_threshold = float(input("Enter the CPU utilization threshold (in %): "))
ram_threshold = float(input("Enter the RAM usage threshold (in MB): "))

def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

def get_cpu_percent_per_core(process):
    """
    Get CPU utilization per core for a process
    """
    num_cores = psutil.cpu_count(logical=True)
    return process.cpu_percent() / num_cores

def process_packet(packet):
    global pid2traffic
    try:
        packet_connection = (packet.sport, packet.dport)
    except (AttributeError, IndexError):
        pass
    else:
        packet_pid = connection2pid.get(packet_connection)
        if packet_pid:
            if packet.src in all_macs:
                pid2traffic[packet_pid][0] += len(packet)
            else:
                pid2traffic[packet_pid][1] += len(packet)

def get_connections():
    global connection2pid
    while is_program_running:
        for c in psutil.net_connections():
            if c.laddr and c.raddr and c.pid:
                connection2pid[(c.laddr.port, c.raddr.port)] = c.pid
                connection2pid[(c.raddr.port, c.laddr.port)] = c.pid
        time.sleep(1)

def print_stats():
    global global_df
    while is_program_running:
        time.sleep(1)
        processes = []
        for process in psutil.process_iter(['pid', 'name']):
            try:
                cpu_percent_per_core = get_cpu_percent_per_core(process)
                if cpu_percent_per_core > 0:  # Only store non-zero CPU usage values
                    pid2cpu_usage_values[process.pid].append(cpu_percent_per_core)

                # Calculate median CPU usage
                try:
                    median_cpu_usage = np.median(pid2cpu_usage_values[process.pid])
                except Exception as e:
                    median_cpu_usage = np.nan  # Set median to NaN if an error occurs


                ram_usage = process.memory_info().rss / (1024 * 1024)  # Convert to MB
                if cpu_percent_per_core >= cpu_threshold or ram_usage >= ram_threshold:
                    # Update CPU usage sum and square sum for the process
                    pid2cpu_usage_sum[process.pid] += cpu_percent_per_core
                    pid2cpu_usage_squaresum[process.pid] += math.pow(cpu_percent_per_core, 2)
                    pid2count[process.pid] += 1

                    # Calculate quadratic deviation
                    quadratic_deviation = 0
                    if pid2count[process.pid] > 1:
                        mean = pid2cpu_usage_sum[process.pid] / pid2count[process.pid]
                        squaresum_mean = pid2cpu_usage_squaresum[process.pid] / pid2count[process.pid]
                        quadratic_deviation = math.sqrt(squaresum_mean - math.pow(mean, 2))

                    traffic = pid2traffic.get(process.pid, [0, 0])
                    upload_speed = (traffic[0] * 60) / 1024  # Convert to KB/min
                    pid2upload_speed_values[process.pid].append(upload_speed)
                    # Calculate median upload speed
                    median_upload_speed = np.median(pid2upload_speed_values[process.pid])
                    download_speed = (traffic[1] * 60) / 1024  # Convert to KB/min
                    processes.append({
                        'pid': process.pid,
                        'name': process.name(),
                        'cpu_percent': cpu_percent_per_core,
                        'median_cpu_percent':median_cpu_usage,
                        'quadratic_deviation': quadratic_deviation,
                        'ram_usage': ram_usage,
                        'upload': traffic[0],
                        'download': traffic[1],
                        'upload_speed': upload_speed,
                        'median_upload': median_upload_speed,  # Add median upload speed metric
                        'download_speed': download_speed
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if processes:
            df = pd.DataFrame(processes)
            df.sort_values("cpu_percent", inplace=True, ascending=False)
            df = df.set_index("pid")
            printing_df = df.copy()
            printing_df["upload"] = printing_df["upload"].apply(get_size)
            printing_df["download"] = printing_df["download"].apply(get_size)
            printing_df["upload_speed"] = printing_df["upload_speed"].apply(lambda s: f"{s:.2f}KB/min")
            printing_df["download_speed"] = printing_df["download_speed"].apply(lambda s: f"{s:.2f}KB/min")
            printing_df["quadratic_deviation"] = printing_df["quadratic_deviation"].apply(lambda x: f"{x:.2f}")
            printing_df["median_cpu_percent"] = printing_df["median_cpu_percent"].apply(lambda x: f"{x:.2f}")  # Format median CPU usage
            printing_df["median_upload"] = printing_df["median_upload"].apply(lambda s: f"{s:.2f}KB/min")  # Format median upload speed
            
            os.system("cls") if "nt" in os.name else os.system("clear")
            print(printing_df.to_string())
            global_df = df
        else:
            print("No processes exceed the set thresholds.")
            return

if __name__ == "__main__":
    printing_thread = Thread(target=print_stats)
    printing_thread.start()
    connections_thread = Thread(target=get_connections)

    connections_thread.start()
    print("Started sniffing")
    sniff(prn=process_packet, store=False)
    is_program_running = False