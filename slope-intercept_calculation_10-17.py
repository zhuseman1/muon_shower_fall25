#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 10:07:24 2025

@author: zacharyhuseman
"""
import pandas as pd
import numpy as np

# === Configuration ===
input_file = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/data_acquisition_10-17.csv"   # path to your raw file
output_file = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/parsed_data_acquisition_10-17.csv"  # path for output CSV

# === Initialize dictionary for all arrays ===
data = {"MasterSync": []}
for i in range(1, 9):
    data[f"{i}_ST"] = []
    data[f"{i}_PT"] = []

# === Read and parse the file ===
with open(input_file, "r") as f:
    lines = f.readlines()[3:]  # skip first 3 lines

for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split(",")
    if len(parts) == 2 and parts[0] == "MasterSync":
        try:
            data["MasterSync"].append(int(parts[1]))
        except ValueError:
            pass
    elif len(parts) == 3:
        id_, dtype, value = parts
        key = f"{id_}_{dtype}"
        if key in data:
            try:
                data[key].append(int(value))
            except ValueError:
                pass

# === Pad columns to equal length ===
max_len = max(len(v) for v in data.values())
for k in data:
    data[k] += [None] * (max_len - len(data[k]))

# === Reorder columns (MasterSync, PTs, STs) ===
ordered_columns = (
    ["MasterSync"] +
    [f"{i}_PT" for i in range(1, 9)] +
    [f"{i}_ST" for i in range(1, 9)]
)
df = pd.DataFrame({col: data[col] for col in ordered_columns})

# === Compute slopes and intercepts for ST vs MasterSync ===
master = np.array(df["MasterSync"], dtype=float)
results = []
for i in range(1, 9):
    st_col = f"{i}_ST"
    st_data = np.array(df[st_col], dtype=float)
    valid = ~np.isnan(master) & ~np.isnan(st_data)
    if np.sum(valid) > 1:
        slope, intercept = np.polyfit(master[valid], st_data[valid], 1)
        results.append((i, slope, intercept))
    else:
        results.append((i, np.nan, np.nan))

df_results = pd.DataFrame(results, columns=["Detector", "Slope", "Intercept"])

# === Combine data and slope/intercept side-by-side ===
if len(df_results) < len(df):
    df_results = pd.concat(
        [df_results, pd.DataFrame([["", "", ""]] * (len(df) - len(df_results)), columns=df_results.columns)],
        ignore_index=True
    )
df_combined = pd.concat([df, df_results], axis=1)

# === Compute calibrated PT times ===
calibrated_data = {}
for i in range(1, 9):
    pt_col = f"{i}_PT"
    slope = df_results.loc[df_results["Detector"] == i, "Slope"].values
    intercept = df_results.loc[df_results["Detector"] == i, "Intercept"].values
    if len(slope) and not np.isnan(slope[0]):
        calibrated_data[f"{i}_PT_cal"] = df[pt_col] * slope[0] + intercept[0]
    else:
        calibrated_data[f"{i}_PT_cal"] = [np.nan] * len(df)

# === Merge calibrated columns into the combined DataFrame ===
for col, values in calibrated_data.items():
    df_combined[col] = values

# === Save to CSV ===
df_combined.to_csv(output_file, index=False)

print(f"✅ Data, slopes/intercepts, and calibrated PT values saved to 'parsed_data_acquisition_10-17.csv'")

