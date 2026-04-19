import pandas as pd

# Load data
df = pd.read_csv('solar_data_race.csv') # Ensure filename matches your local file
df['period_end'] = pd.to_datetime(df['period_end'])

# Constants (m = 250 kg)
m, Cd, A, Crr = 250, 0.118, 1, 0.012 
eff_motor, eff_solar, eff_mppt = 0.95, 0.21, 0.98
A_solar, batt_cap = 6.0, 3.1
target_dist = 3022 

def simulate_real(v_kmh):
    v_ms = v_kmh / 3.6
    # Power required in Watts
    P_req = (0.5 * 1.225 * Cd * A * (v_ms**3) + m * 9.81 * Crr * v_ms) / eff_motor
    
    energy = batt_cap
    dist_covered = 0
    daily_logs = []
    
    for _, row in df.iterrows():
        t = row['period_end']
        dt = 10/60 # hours
        e_in = (row['GHI'] * A_solar * eff_solar * eff_mppt * dt) / 1000
        
        e_out = 0
        if 8 <= t.hour < 17 and dist_covered < target_dist:
            needed = (P_req * dt) / 1000
            # REALISTIC CHECK: Only move if energy is available
            if (energy + e_in) >= needed:
                e_out = needed
                dist_covered += v_kmh * dt
            else:
                # Car is out of energy and stops/crawls
                e_out = energy + e_in 
        
        energy = min(batt_cap, max(0, energy + e_in - e_out))
        
        # Log energy at the end of the driving day (17:00)
        if t.hour == 17 and t.minute == 0:
            daily_logs.append((t.date(), energy))
            
    return daily_logs, dist_covered

# Execution for speeds
for s in [67.16, 77.16, 87.16]:
    logs, final_d = simulate_real(s)
    print(f"\n--- Speed: {s} km/h ---")
    
    # Print energy at end of EACH day
    for day_date, energy_val in logs:
        print(f"End of {day_date}: {energy_val:.3f} kWh remaining")
        
    print(f"Final Distance Covered: {final_d:.1f} km")
    print(f"Race Finished: {'YES' if final_d >= target_dist else 'FAILED'}")