import psutil
import time
import subprocess

# Monitor the overall CPU usage
def monitor_cpu_usage():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        print("CPU Usage: {}%".format(cpu_usage))
        
        if cpu_usage > 10:
            # Stop the current script
            break
        
        time.sleep(1)

    # Trigger newinteg.py considering the fact that it has user inputs 
    # and the user can provide the inputs to the script
    subprocess.run(["python", "newinteg.py"])
    

if __name__ == "__main__":
    monitor_cpu_usage()
