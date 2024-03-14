from scapy.all import *
import psutil
from collections import defaultdict
import os
from threading import Thread
import pandas as pd
from datetime import datetime
import time

# get all network adapter's MAC addresses
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

def print_pid2traffic(upload_threshold):
    global global_df
    processes = []
    for pid, traffic in pid2traffic.items():
        try:
            p = psutil.Process(pid)
        except psutil.NoSuchProcess:
            continue
        name = p.name()
        try:
            create_time = datetime.fromtimestamp(p.create_time())
        except OSError:
            create_time = datetime.fromtimestamp(psutil.boot_time())
        
        # Check if PID exists in global_df before accessing
        upload_speed = traffic[0] - global_df.at[pid, "Upload"] if global_df is not None and pid in global_df.index else traffic[0]
        download_speed = traffic[1] - global_df.at[pid, "Download"] if global_df is not None and pid in global_df.index else traffic[1]
        
        # Convert the upload and download speeds to KB/min
        upload_speed = (upload_speed * 60) / 1024
        download_speed = (download_speed * 60) / 1024
        if upload_speed >= upload_threshold:
            process = {
                "pid": pid, "name": name, "create_time": create_time, "Upload": traffic[0],
                "Download": traffic[1], "Upload Speed": upload_speed, "Download Speed": download_speed
            }
            processes.append(process)
    
    # Only proceed if there are processes to consider
    if processes:
        df = pd.DataFrame(processes)
        df = df.set_index("pid")
        df.sort_values("Download", inplace=True, ascending=False)
        printing_df = df.copy()
        printing_df["Download"] = printing_df["Download"].apply(get_size)
        printing_df["Upload"] = printing_df["Upload"].apply(get_size)
        printing_df["Download Speed"] = printing_df["Download Speed"].apply(lambda s: f"{s:.2f}KB/min")
        printing_df["Upload Speed"] = printing_df["Upload Speed"].apply(lambda s: f"{s:.2f}KB/min")
        os.system("cls") if "nt" in os.name else os.system("clear")
        print(printing_df.to_string())
        global_df = df
    else:
        print("No processes exceed the upload threshold.")
        return  # Exit the function if there are no processes

def print_stats(upload_threshold):
    while is_program_running:
        time.sleep(1)
        print_pid2traffic(upload_threshold)

if __name__ == "__main__":
    upload_threshold_kb_min = float(input("Enter the upload threshold (in KB/min): "))
    upload_threshold_bytes_min = upload_threshold_kb_min * 1024 / 60  # Convert KB/min to bytes/min
    printing_thread = Thread(target=print_stats, args=(upload_threshold_bytes_min,))
    printing_thread.start()
    connections_thread = Thread(target=get_connections)
    connections_thread.start()
    print("Started sniffing")
    sniff(prn=process_packet, store=False)
    is_program_running = False
