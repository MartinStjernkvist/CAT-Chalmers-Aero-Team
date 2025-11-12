#%%
import numpy as np

V = 4 * 10**(-3) # volume of tank in m^3
h = 0.15 # height of tank in meters

A_tank = V / h # area of tank, box shape

g = 9.81 # grativy constant

distance = 150 # double-check
velocity = 15 # cruise

t = distance / velocity # time between waypoints

Cd = 0.9 # discharge coefficient

def diameter(A_tank, h, t):
    A_outlet = A_tank / (Cd * g * t) * np.sqrt(2 * g * h)
    # A_outlet = 2 * V / (Cd * t * np.sqrt(2 * g * h)) 
    r = np.sqrt(A_outlet / np.pi)
    d = r * 2
    return d

d = diameter(A_tank, h, t)
print('diameter', f'{d * 1000:.1f}', ' mm')
#%%


