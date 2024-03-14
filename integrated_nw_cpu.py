import os
import math
import time
import psutil
from scapy.all import *
from collections import defaultdict
from threading import Thread
import pandas as pd
from datetime import datetime

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

pid2count = defaultdict(int)

# The global Pandas DataFrame that's used to track previous traffic stats
global_df = None

# Global boolean for program status
is_program_running = True


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


def get_all_processes():
    """
    Retrieve information on all running processes with CPU usage sum updated
    """
    processes = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            cpu_percent_per_core = get_cpu_percent_per_core(process)

            # Update CPU usage sum and square sum for the process
            pid2cpu_usage_sum[process.pid] += cpu_percent_per_core
            pid2cpu_usage_squaresum[process.pid] += math.pow(cpu_percent_per_core, 2)
            if int(cpu_percent_per_core) != 0:
                pid2count[process.pid]+=1

            # Handle potential division by zero with default value (0)
            # vcount = pid2count.get(process.pid, 0)  # Get count or set to 0 if not found
            quadratic_deviation = 0 if int(pid2count[process.pid]) == 0 else (math.pow(abs(((pid2cpu_usage_squaresum[process.pid] / pid2count[process.pid])-math.pow((pid2cpu_usage_sum[process.pid]/pid2count[process.pid]),2))),0.5))

            memory_usage_mb = process.memory_info().rss / (1024 * 1024)
            traffic = pid2traffic.get(process.pid, [0, 0])
            processes.append({
                'pid': process.pid,
                'name': process.name(),
                'cpu_percent': cpu_percent_per_core,
                'quadratic_deviation': quadratic_deviation,
                # 'cpu_usage_sum': pid2cpu_usage_sum[process.pid],
                # 'cpu_usage_squaresum': pid2cpu_usage_squaresum[process.pid],
                # 'count': pid2count[process.pid],
                'memory_usage_mb': memory_usage_mb,
                'upload': traffic[0],
                'download': traffic[1]
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


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
        processes = get_all_processes()
        df = pd.DataFrame(processes)
        try:
            # Sort by cpu_percent in descending order (highest first)
            df.sort_values("cpu_percent", inplace=True, ascending=False)
            df = df.set_index("pid")  # Set index to pid
        except KeyError as e:
            pass
        printing_df = df.copy()
        try:
            printing_df["download"] = printing_df["download"].apply(get_size)
            printing_df["upload"] = printing_df["upload"].apply(get_size)
            # Convert CPU usage sum to a percentage (optional)
            # printing_df["cpu_usage_sum"] = printing_df["cpu_usage_sum"].apply(lambda x: f"{x:.2f}%")
            printing_df["quadratic_deviation"] = printing_df["quadratic_deviation"].apply(lambda x: f"{x:.2f}")
        except KeyError as e:
            pass
        os.system("cls") if "nt" in os.name else os.system("clear")
        print(printing_df.to_string())
        global_df = df

if __name__ == "__main__":
    printing_thread = Thread(target=print_stats)
    printing_thread.start()
    connections_thread = Thread(target=get_connections)
    connections_thread.start()
    print("Started sniffing")
    sniff(prn=process_packet, store=False)
    is_program_running = False
