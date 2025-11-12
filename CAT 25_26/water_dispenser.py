#%%
import numpy as np

V = 4 * 10**(-3) # m^3
h = 0.20 # m

A_tank = V / h

g = 9.81

distance = 150
velocity = 15

t = distance / velocity

Cd = 0.6

def r(A_tank, h, t):
    A_outlet = 2 * A_tank * np.sqrt(h) / (t * Cd * np.sqrt(2 * g))
    r = np.sqrt(A_outlet / np.pi)
    return r

radius = r(A_tank, h, t)
print('radius', radius * 1000, ' mm')
#%%


