#%%
import numpy as np
# eta = efficiency
# cap = capacity
# prop = propeller

#===================================================================================================
# REQUIREMENTS / MAIN ASSUMPTIONS
#===================================================================================================
m = 10 # kg
g = 9.82

# Lift
L = m * g
L_D_ratio = 9

# Battery
battery_cap_Ah = 6 # Ah
voltage = 22.2 # V
battery_cap_Wh = battery_cap_Ah * voltage
leftover_cap_factor = 0.2

# Efficiencies
eta_batteries = 0.8
eta_prop = 0.6
eta_motor_ESC = 0.85

# total distance 
distance_lap = 2 * 2_800 # m

# Cruise speeds
v_cruise_slow = 12.5 # m/s
v_cruise_fast = 20
v_wind = 20 * 0.4

#===================================================================================================
# CALCULATIONS
#===================================================================================================
D = L / L_D_ratio
print(f'\ndrag: \n{D:.2f} N')

usable_cap = battery_cap_Wh * (1 - leftover_cap_factor)
print(f'\nusable battery capacity: \n{usable_cap:.2f} Wh')

eta_tot = eta_prop * eta_motor_ESC * eta_batteries
print(f'\ntotal efficiency: \n{eta_tot:.2f} %')

def cruise(v_cruise):
    v_actual = v_cruise - v_wind
    P_ideal = D * v_cruise
    
    P_actual = P_ideal / eta_tot
    print(f'power required: \n{P_actual:.2f} W')
    
    flight_time_h = usable_cap / P_actual
    print(f'flight time: \n{flight_time_h * 60:.2f} min')
    
    distance = (v_actual +  v_cruise) / 2 * flight_time_h * 3600
    print(f'distance flown: \n{distance:.2f} m')
    
    if distance <= distance_lap:
        print('Mission failed')
        
# Slow case
print('\nSLOW CASE')
v_cruise = v_cruise_slow
cruise(v_cruise)

# Fast case
print('\nFAST CASE')
v_cruise = v_cruise_fast
cruise(v_cruise)