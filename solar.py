import pandas as pd
import re

# Characteristics from instructions
V_MP_CELL = 0.755
I_MP_STC = 5.51
V_DIODE = 0.9
EFF_MPPT = 0.985
SUBSTRINGS = [(1, 22), (23, 44), (45, 66)]

def parse_cells(s):
    if pd.isna(s) or s.strip() == '-': return set()
    cells = set()
    for part in re.split(r'[,\s]+', s.strip()):
        if '-' in part:
            start, end = map(int, part.split('-'))
            cells.update(range(start, end + 1))
        else: cells.add(int(part))
    return cells

df = pd.read_csv('Shading data - Sheet1.csv')

print(f"{'Timestamp':<10} | {'Power (W)':<10}")
print("-" * 25)
totalpower=0


for _, row in df.iterrows():
    G = row['Irradiance (W/m^2)']
    if G == 0: continue 
    
    shaded = parse_cells(str(row['Shaded cells']))
    current = I_MP_STC * (G / 1000.0)
    v_total = 0
    
    for start, end in SUBSTRINGS:
        if any(start <= c <= end for c in shaded):
            v_total -= V_DIODE
        else:
            v_total += (end - start + 1) * V_MP_CELL
            
    power = max(0.0, v_total * current * EFF_MPPT)
    totalpower += power
    print(f"{row['Timestamp']:<10} | {round(power, 2):<10}")

print("Total power generated through out the day is: ",totalpower)