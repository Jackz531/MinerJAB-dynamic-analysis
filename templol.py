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
import subprocess

start_time = 0
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
pid2network_rate_values = defaultdict(list)

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
    # Set to keep track of logged PIDs to avoid duplicates
    global is_program_running
    
    # save stats to int.csv afteer 40s, while the printing to console
    while is_program_running:
        time.sleep(1)
        print_statsmain()
        if (datetime.now() - start_time).total_seconds() > 29:

            global_df.to_csv("int.csv",mode='a',header=False)
            #is_program_running=False
            #subprocess.run(['python', 'libcalls.py'])
            time.sleep(5)
            
        if (datetime.now() - start_time).total_seconds() > 70:
            is_program_running=False
            


def print_statsmain():
    global global_df
    logged_pids = set()
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
                    # print("\n",process.pid,traffic[0],"\n")
                    try:
            # calculate the upload and download speeds by simply subtracting the old stats from the new stats
                        upload_speed = traffic[0] - global_df.at[process.pid, "upload"]
                        download_speed = traffic[1] - global_df.at[process.pid, "download"]
                    except (KeyError, AttributeError):
                        # If it's the first time running this function, then the speed is the current traffic
                        # You can think of it as if old traffic is 0
                        print("Errorlol\n")
                        upload_speed = traffic[0]
                        download_speed = traffic[1]

                    # elapsed_time = (datetime.now() - start_time).total_seconds()
                    # upload_speed = (traffic[0] / elapsed_time) * (60 / 1024)  # Convert to KB/min
                    network_rate = upload_speed + download_speed
                    if network_rate>0:
                        pid2network_rate_values[process.pid].append(network_rate)
                    # Calculate median network rate
                    median_network_rate = np.median(pid2network_rate_values[process.pid])

                    # download_speed = (traffic[1] / elapsed_time) * (60 / 1024) # Convert to KB/min
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
                        'median_network_rate': median_network_rate,  # Add median network metric
                        'download_speed': download_speed
                    })
                    
                    # Log the PID of the process if CPU utilization is above the threshold and not already logged
                    #create log.txt if it is not there.
                    if not os.path.exists("log.txt"):
                        with open("log.txt", "w"):
                            pass
                        
                    if cpu_percent_per_core >= cpu_threshold and process.pid not in logged_pids and process.pid != 0:
                        with open("log.txt", "a") as log_file:
                            log_file.write(f"{process.pid}\n")
                        logged_pids.add(process.pid)
                    
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
        printing_df["median_network_rate"] = printing_df["median_network_rate"].apply(lambda s: f"{s:.2f}KB/min")  # Format median upload speed
            
        os.system("cls") if "nt" in os.name else os.system("clear")
        print(printing_df.to_string())
        global_df = df
    else:
        print("No processes exceed the set thresholds.")


if __name__ == "__main__":
    printing_thread = Thread(target=print_stats)
    printing_thread.start()
    connections_thread = Thread(target=get_connections)

    connections_thread.start()
    print("Started sniffing")
    start_time=datetime.now()
    sniff(prn=process_packet, store=False)
    is_program_running = False
