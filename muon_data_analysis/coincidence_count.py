#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 11:45:46 2025

@author: zacharyhuseman
"""

import pandas as pd

# === USER SETTINGS ===
filename = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/sorted_data_acquisition_10-17.csv"   # <-- change if needed
threshold_us = 400                                # value in microseconds


# === LOAD DATA ===
try:
    df = pd.read_csv(filename)
except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    raise SystemExit

# Convert delta_t column to numeric (drops invalid values)
delta_t = pd.to_numeric(df["delta_t"], errors="coerce").dropna()

# === CHECK IF ANY VALID VALUES EXIST ===
total_values = len(delta_t)
print(f"Total valid delta_t values: {total_values}")

if total_values == 0:
    print("No coincidences found (no usable delta_t values).")
else:
    count_le = (delta_t <= threshold_us).sum()
    percentage = (count_le / total_values) * 100
    
    print(f"Threshold value: {threshold_us} µs")
    print(f"Count ≤ threshold: {count_le}")
    print(f"Percentage: {percentage:.2f}%")
