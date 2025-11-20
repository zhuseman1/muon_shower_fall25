#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 16 11:25:34 2025

@author: zacharyhuseman
"""

# === Robust standardizer that writes MasterSync as two columns ===

input_file = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/syncing_measurement_test_9-19_1.csv"
output_file = "/Users/zacharyhuseman/Desktop/Research/muon_data_csv/syncing_measurement_test_9-19_1_fixed.csv"

def to_int_string(token):
    """Try to convert token to integer string. If token is float-like, truncate decimals.
       If conversion fails, return the original stripped token."""
    t = token.strip()
    if t == "":
        return t
    try:
        # handle floats that look like '1.000000e+07' or '12345.0'
        v = float(t)
        iv = int(v)
        return str(iv)
    except Exception:
        return t

fixed_lines = []
with open(input_file, "r") as f:
    lines = f.readlines()

for line in lines:
    # keep original exact line if it's a comment or empty
    if line.strip() == "" or line.lstrip().startswith("#"):
        fixed_lines.append(line)
        continue

    parts = [p for p in line.rstrip("\n").split(",")]
    # normalize whitespace for detection
    first = parts[0].strip() if len(parts) >= 1 else ""

    # If this is a MasterSync line (detect 'MasterSync' in first field)
    if first == "MasterSync":
        # find the last non-empty token that likely holds the timestamp
        # prefer parts[1] if present, otherwise last element
        ts_token = ""
        if len(parts) >= 2 and parts[1].strip() != "":
            ts_token = parts[1].strip()
        else:
            # scan from right for first non-empty token
            for tok in reversed(parts):
                if tok.strip() != "":
                    ts_token = tok.strip()
                    break
        ts_int_str = to_int_string(ts_token)
        fixed_lines.append(f"MasterSync,{ts_int_str}\n")
    else:
        # not MasterSync: keep line exactly as-is (preserves ST/PT lines)
        fixed_lines.append(line)

with open(output_file, "w") as f:
    f.writelines(fixed_lines)

print(f"✅ Wrote fixed file to: {output_file}")



