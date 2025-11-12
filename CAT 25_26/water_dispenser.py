#%%
import numpy as np

V = 4 * 10**(-3) # m^3
h = 0.15 # m

# A_tank = V / h

g = 9.81

distance = 150
velocity = 15

t = distance / velocity

Cd = 0.9

def d(V, h, t):
    # A_outlet = A_tank / (g * t) * np.sqrt(2 * g * h)
    A_outlet = 2 * V / (Cd * t * np.sqrt(2 * g * h)) 
    r = np.sqrt(A_outlet / np.pi)
    d = r * 2
    return d

diameter = d(V, h, t)
print('diameter', f'{diameter * 1000:.1f}', ' mm')
#%%


