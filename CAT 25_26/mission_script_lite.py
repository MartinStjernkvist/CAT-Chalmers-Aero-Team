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
rho_air = 1.225 # kg/m^3

# Lift
L = m * g
L_D_ratio = 9
CL_max = 1.8
CD = 0.05

wingspan = 2.5
chord = 0.345

takeoff_margin = 0.1
mu = 0.3 # grass and rubber
l_runway = 20

# for g/W method
thrust_to_weight_takeoff = 0.5

# Battery
battery_cap_Ah = 6 # Ah
voltage = 22.2 # V
battery_cap_Wh = battery_cap_Ah * voltage
leftover_cap_factor = 0.2

# Efficiencies
eta_batteries = 0.8
eta_prop = 0.6
eta_motor_ESC = 0.85
eta_motor_takeoff = 4.10 # g/W, 90% throttle
e = 0.8 # Oswald efficiency, rectangular wing

# total distance 
distance_lap = 2 * 2_800 # m

# Cruise speeds
v_cruise_slow = 12.5 # m/s
v_cruise_fast = 20
v_wind = 20 * 0.4

#===================================================================================================
# CALCULATIONS
#===================================================================================================
S = wingspan * chord
AR = wingspan**2 / S

v_stall = np.sqrt(2 * L / (rho_air * S * CL_max))
print(f'\nstall speed: \n{v_stall:.2f} m/s')

v_takeoff = (1 + takeoff_margin) * v_stall
print(f'\ntake-off speed: \n{v_takeoff:.2f} m/s')

CL_takeoff = CL_max / (1 + takeoff_margin)**2

CD_induced = CL_takeoff**2 / (np.pi * AR * e)
print(f'\ninduced drag coefficient \n{CD_induced:.2f}')

CD_tot = CD + CD_induced
print(f'\ntotal drag coefficient \n{CD_tot:.2f} N')

D_takeoff = 1/2 * rho_air * v_takeoff**2 * S * CD_tot
print(f'\ndrag during take-off: \n{D_takeoff:.2f}')

F_fric = mu * L

a_takeoff = v_takeoff**2 / (2 * l_runway)
print(f'\nacceleration at take-off: \n{a_takeoff:.2f} m/s^2')

F_acc_takeoff = m * a_takeoff
print(f'\nforce from acceleration at take-off \n{F_acc_takeoff:.2f} N')

T_takeoff = D_takeoff + F_fric + F_acc_takeoff
print(f'\nthrust at take-off: \n{T_takeoff:.2f} N')

# T_target = thrust_to_weight_takeoff * L
# print(f'\nthrust at take-off (calculated with thrust-to-weight ratio): \n{T_target:.2f} N')

P_out_takeoff = T_takeoff * v_takeoff
print(f'\npower delivered to air at take-off: \n{P_out_takeoff:.2f} W')

P_electrical_takeoff = P_out_takeoff / (eta_prop * eta_motor_ESC)
print(f'\nactual electrical power at take-off: \n{P_electrical_takeoff:.2f} W')

P_g_per_W =  T_takeoff * (1000 / g) / eta_motor_takeoff
print(f'\nactual electrical power at take-off (g/W method): \n{P_g_per_W:.2f} W')

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