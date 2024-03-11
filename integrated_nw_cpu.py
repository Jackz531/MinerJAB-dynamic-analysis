import os
import time
import psutil
from scapy.all import *
from collections import defaultdict
from threading import Thread
import pandas as pd
from datetime import datetime

# get the all network adapter's MAC addresses
all_macs = {iface.mac for iface in ifaces.values()}
# A dictionary to map each connection to its corresponding process ID (PID)
connection2pid = {}
# A dictionary to map each process ID (PID) to total Upload (0) and Download (1) traffic
pid2traffic = defaultdict(lambda: [0, 0])
# the global Pandas DataFrame that's used to track previous traffic stats
global_df = None
# global boolean for status of the program
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
    # Get the number of CPU cores
    num_cores = psutil.cpu_count(logical=True)
    # Calculate the CPU utilization per core
    return process.cpu_percent() / num_cores

def get_all_processes():
    # Retrieve all processes with their CPU, memory, and network usage
    processes = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            cpu_percent_per_core = get_cpu_percent_per_core(process)
            traffic = pid2traffic.get(process.pid, [0, 0])
            processes.append({
                'pid': process.pid,
                'name': process.name(),
                'cpu_percent': cpu_percent_per_core,
                'memory_percent': process.memory_percent(),
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
            df = df.set_index("pid")
            df.sort_values("download", inplace=True, ascending=False)
        except KeyError as e:
            pass
        printing_df = df.copy()
        try:
            printing_df["download"] = printing_df["download"].apply(get_size)
            printing_df["upload"] = printing_df["upload"].apply(get_size)
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
