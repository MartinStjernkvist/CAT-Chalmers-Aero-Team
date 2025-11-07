import numpy as np
pi = np.pi
mm3_to_dm3 = (1/100)**3

alpha = 40
hyp = 570
len = hyp / np.cos(alpha)
print(len)

diameter = 380 # mm
width = 1720 # mm

volume_cylinder = (diameter/2)**2 * pi * width * mm3_to_dm3 # L
print(volume_cylinder)

x = 4.5
y = 1.8
c = np.sqrt(x**2 + y**2)
radius_propeller = c - 3.5/2
print(radius_propeller)