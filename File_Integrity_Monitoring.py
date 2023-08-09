import os
import hashlib
import tkinter as tk
from tkinter import filedialog
import time
import signal
import sys


def calculate_file_hash(filepath):
    with open(filepath, "rb") as f:
        file_content = f.read()
        filehash = hashlib.sha512(file_content).hexdigest()
    return filehash


def erase_baseline_if_already_exists():
    if os.path.exists("./baseline.txt"):
        os.remove("./baseline.txt")


def select_directory():
    root = tk.Tk()
    root.withdraw()
    selected_directory = filedialog.askdirectory(title="Select the directory to be monitored")
    return selected_directory


def signal_handler(sig, frame):
    print("\nMonitoring stopped by user.")
    sys.exit(0)


# Register the signal handler for Ctrl + C (SIGINT)
signal.signal(signal.SIGINT, signal_handler)


def create_baseline(directory):
    baseline_data = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_file_hash(file_path)
            baseline_data[file_path] = file_hash
    return baseline_data


# Create a GUI for the user to select the directory to be monitored
selected_directory = select_directory()

# Check if a directory was selected
if not selected_directory:
    print("No directory selected. Exiting...")
    exit()

print(f"Selected Directory: {selected_directory}")

response = input("Do you want to begin monitoring files in this directory? (Y/N): ")

if response.upper() == "Y":
    # Delete baseline.txt if it already exists
    erase_baseline_if_already_exists()

    # Calculate Hash from the target files and store in baseline.txt
    baseline_file = open("./baseline.txt", "a")

    baseline_data = create_baseline(selected_directory)

    for file_path, file_hash in baseline_data.items():
        baseline_file.write(f"{file_path}|{file_hash}\n")

    baseline_file.close()

    print("Baseline collected and monitoring initiated.")

    change_detected = False

    # Continuously monitor the selected directory
    while True:
        time.sleep(1)

        current_baseline_data = create_baseline(selected_directory)

        # Check for new files, file changes, and deleted files
        for file_path, file_hash in current_baseline_data.items():
            if file_path not in baseline_data:
                change_detected = True
                print(f"{file_path} has been created or changed or deleted!")

            elif baseline_data[file_path] != file_hash:
                change_detected = True
                print(f"{file_path} has been created or changed or deleted!")

        baseline_data = current_baseline_data

        # Stop printing if change detected until another change occurs
        if change_detected:
            change_detected = False
            time.sleep(3)  # Stop printing for 3 seconds

else:
    print("Monitoring canceled. Exiting...")
