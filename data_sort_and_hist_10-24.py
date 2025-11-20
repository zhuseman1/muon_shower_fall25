#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 11:09:01 2025

@author: zacharyhuseman
"""

import pandas as pd
import matplotlib.pyplot as plt

# === Configuration ===
input_file = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/parsed_data_acquisition_10-17.csv"
output_file = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/sorted_data_acquisition_10-17.csv"
histogram_file = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/delta_t_histogram_10-17.png"

# === Specify x axis ===
# based on what we want the x axis to be and the largest delta_t value (typically 1 sec)
# 1_000_000 = 1 sec
run_time_us =  1_000_000

# === Load data ===
df = pd.read_csv(input_file)

# === Collect all PT calibration columns ===
pt_columns = [f"{i}_PT_cal" for i in range(1, 9) if f"{i}_PT_cal" in df.columns]

if not pt_columns:
    raise ValueError("No columns labeled '1_PT_cal' through '8_PT_cal' found in the file.")

# === Stack all PT columns into one Series ===
combined = pd.concat([df[col] for col in pt_columns], ignore_index=True)

# === Drop NaN, sort, and round to 3 decimals ===
combined = combined.dropna().sort_values().round(3).reset_index(drop=True)

# === Compute delta_t (difference between consecutive timestamps) ===
delta_t = combined.diff().shift(-1).round(3)

# === Combine into one DataFrame ===
result = pd.DataFrame({
    "PT_cal": combined,
    "delta_t": delta_t
})

# === Save as CSV ===
result.to_csv(output_file, index=False, float_format="%.3f")

print(f"Condensed data with Δt saved to: {output_file}")
print(result.head(10))

# === Plot histogram of delta_t ===
plt.figure(figsize=(8, 5))
plt.hist(delta_t.dropna(), bins=750, color='steelblue', edgecolor='black', alpha=0.7) # change bin size based on desired width of bin
# (run_time_us)/(# of bins) = bin width
plt.title("Histogram of Δt Values", fontsize=14)
plt.xlabel("Δt (microseconds)", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# === Set x-axis range based on run time in microseconds ===
plt.xlim(0, run_time_us)

plt.tight_layout()

# === Save histogram ===
plt.savefig(histogram_file, dpi=300)
plt.close()

print(f"Histogram saved to: {histogram_file}")


