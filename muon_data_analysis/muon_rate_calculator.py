#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 11:11:54 2025

@author: zacharyhuseman
"""

filename = "/Users/zacharyhuseman/Downloads/detector_1A_rate_trial.csv"  # Change path if needed

# Read file
with open(filename, "r") as f:
    lines = f.read().splitlines()

pt_timestamps = []

for line in lines:
    parts = line.strip().split(",")
    
    # Only accept valid PT rows with 3 fields
    if len(parts) == 3:
        index, dtype, value = parts
        
        # Filter for PT only
        if dtype == "PT":
            try:
                timestamp = int(value)
                pt_timestamps.append(timestamp)
            except ValueError:
                pass  # ignore non-numeric rows

# Sanity checks
if len(pt_timestamps) < 2:
    raise ValueError("Not enough PT events found to compute elapsed time.")

# Compute total PT events
total_events = len(pt_timestamps)

# Compute elapsed time in seconds
start_time = min(pt_timestamps)
end_time = max(pt_timestamps)
elapsed_us = end_time - start_time
elapsed_s = elapsed_us / 1_000_000  # convert to seconds

# Compute muon rate (events per second)
muon_rate = total_events / elapsed_s

print("\n===== MUON RATE RESULTS =====")
print(f"Total PT Events: {total_events}")
print(f"Elapsed Time (s): {elapsed_s:.6f}")
print(f"Muon Rate (events/s): {muon_rate:.6f}")
print(f"Muon Rate (events/min): {muon_rate*60:.6f}")
print(f"Muon Rate (events/hour): {muon_rate*3600:.6f}")
