#%%
import numpy as np

"""
INPUTS
"""
# Height of all cylinders
height = 150 * 10**-3 # m

# Diameter of cylinders at the front
diam_front_inner = 100 * 10**-3 # m
diam_front_outer = 100 * 10**-3 # m

# Distances from CoG (1/4 chord length)
arm_front_inner = 100 * 10**-3 # m

# Factor that multiplies the arm distances
inner_factor = 2.5
outer_factor = 1.65

"""
CALCULATIONS
"""
arm_front_outer = arm_front_inner + diam_front_inner / 2 + diam_front_outer / 2

arm_back_inner = arm_front_inner * inner_factor
arm_back_outer = arm_front_outer * outer_factor

"""
moment equilibrium about CoG point
for example: v_front_inner * arm_front_inner = v_back_inner * arm_back_inner
"""
volume_front_inner = (diam_front_inner / 2)**2 * np.pi * height
volume_back_inner = volume_front_inner * arm_front_inner / arm_back_inner
radius_back_inner = np.sqrt(volume_back_inner / (np.pi * height))
diam_back_inner = 2 * radius_back_inner

volume_front_outer = (diam_front_outer / 2)**2 * np.pi * height
volume_back_outer = volume_front_outer * arm_front_outer / arm_back_outer
radius_back_outer = np.sqrt(volume_back_outer / (np.pi* height))
diam_back_outer = 2 * radius_back_outer

print('\nCylinder volumes:')
print('volume_front_inner', f'{volume_front_inner * 1000:.2f}', 'L')
print('volume_front_outer', f'{volume_front_outer * 1000:.2f}', 'L')
print('volume_back_inner', f'{volume_back_inner * 1000:.2f}', 'L')
print('volume_back_outer', f'{volume_back_outer * 1000:.2f}', 'L')

sum = volume_back_inner + volume_back_outer + volume_front_inner + volume_front_outer
print('total volume: ', f'{sum * 1000:.2f}', 'L')

print('\nDistances from CoG to midpoint of cylinders:')
print('arm_front_inner: ', arm_front_inner * 1000, 'mm')
print('arm_front_outer: ', arm_front_outer * 1000, 'mm')
print('arm_back_inner: ', arm_back_inner * 1000, 'mm')
print('arm_back_outer: ', arm_back_outer * 1000, 'mm')

print('\nCylinder diameters:')
print('diam_back_inner: ', f'{diam_back_inner * 1000:.2f}', 'mm')
print('diam_back_outer: ', f'{diam_back_outer * 1000:.2f}', 'mm')

value = arm_back_outer - arm_back_inner - diam_back_inner/2 - diam_back_outer/2

print('\nDoes it fit?')
if value > 0:
    print('yes, remaining distance between cyilders is', f'{value * 1000:.2f}', 'mm')
else: 
    print('no')
#%%