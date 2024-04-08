from scapy.all import *
import psutil
from collections import defaultdict
import os
from threading import Thread
import pandas as pd
from datetime import datetime
import time
import statistics

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

def get_size(bytes, seconds=60):
    """
    Returns size of bytes in kilobytes per minute
    """
    kilobytes = bytes / 1024
    return f"{kilobytes / seconds:.2f}KB/min"

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

# A list to store non-zero upload speeds
non_zero_upload_speeds = []

def print_pid2traffic():
    global global_df, non_zero_upload_speeds
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
        upload_speed = traffic[0] * 60 / 1024  # Convert to KB/min
        if upload_speed > 0:
            non_zero_upload_speeds.append(upload_speed)
            if len(non_zero_upload_speeds) > 40:
                non_zero_upload_speeds.pop(0)  # Keep only the last 40 non-zero upload speeds
        process = {
            "pid": pid, "name": name, "create_time": create_time,
            "Upload": traffic[0], "Download": traffic[1],
            "Upload Speed": upload_speed,  # Already in KB/min
            "Download Speed": traffic[1] * 60 / 1024  # Convert to KB/min
        }
        processes.append(process)
    df = pd.DataFrame(processes)
    try:
        df = df.set_index("pid")
        df.sort_values("Download", inplace=True, ascending=False)
    except KeyError:
        pass
    printing_df = df.copy()
    try:
        printing_df["Download"] = printing_df["Download"].apply(get_size)
        printing_df["Upload"] = printing_df["Upload"].apply(get_size)
        printing_df["Download Speed"] = printing_df["Download Speed"].apply(get_size)
        printing_df["Upload Speed"] = printing_df["Upload Speed"].apply(get_size)
    except KeyError:
        pass
    os.system("cls") if "nt" in os.name else os.system("clear")
    print(printing_df.to_string())
    global_df = df

def print_stats():
    while is_program_running:
        time.sleep(1)
        print_pid2traffic()

if __name__ == "_main_":
    printing_thread = Thread(target=print_stats)
    printing_thread.start()
    connections_thread = Thread(target=get_connections)
    connections_thread.start()
    print("Started sniffing")
    sniff(prn=process_packet, store=False)
    start_time = time.time()
    while time.time() - start_time < 40:  # Monitor for 40 seconds
        pass
    is_program_running = False
    printing_thread.join()
    connections_thread.join()
    # Print the final median upload speed
    if non_zero_upload_speeds:
        print(f"Median Upload Speed: {statistics.median(non_zero_upload_speeds):.2f}KB/min")
    else:
        print("Median Upload Speed: N/A")