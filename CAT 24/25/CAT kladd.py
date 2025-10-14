import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from mpl_toolkits import mplot3d

pi = np.pi

AR = 17.5
L = 400
chord = L / AR
thickness_percent = 0.08
thickness = thickness_percent * chord
# print(thickness)

# print(4000/230)

"""
Half ellipse with cylinder payload vs Cirkel with square payload vs Ellipse with cylinder payload
"""
offset_wood = 15

diameter_circle_fuselage = 300
radius_circle_fuselage = diameter_circle_fuselage / 2

height_ellipse_fuselage = 450
width_ellipse_fuselage = 350

'''front area'''
# circle fuselage
front_area_circle_fuselage = pi * radius_circle_fuselage ** 2
# print(f'front_area_circle_fuselage: {front_area_circle_fuselage}')

# half ellipse fuselage
ellipse_part_area = (pi * (height_ellipse_fuselage / 2) * (width_ellipse_fuselage / 2)) / 2  # half ellipse
circle_part_area = (pi * (width_ellipse_fuselage / 2) ** 2) / 2  # half circle

front_area_ellipse_fuselage = ellipse_part_area + circle_part_area
print(f'front_area_ellipse_fuselage: {front_area_ellipse_fuselage}')

# full ellipse
front_area_full_ellipse_fuselage = 2 * ellipse_part_area

'''volume'''
# circle fuselage
volume_payload_circle_fuselage = (diameter_circle_fuselage - 2 * offset_wood) ** 2 / 2
# print(f'\nvolume_payload_circle_fuselage: {volume_payload_circle_fuselage}')

# half ellipse fuselage
volume_payload_ellipse_fuselage = pi * ((width_ellipse_fuselage - 2 * offset_wood) / 2) ** 2
print(f'volume_payload_ellipse_fuselage: {volume_payload_ellipse_fuselage}')

# full ellipse
volume_payload_full_ellipse_fuselage = volume_payload_ellipse_fuselage

'''volume utilization'''
volume_utilization_cicrle_fuselage = volume_payload_circle_fuselage / front_area_circle_fuselage
volume_utilization_ellipse_fuselage = volume_payload_ellipse_fuselage / front_area_ellipse_fuselage
volume_utilization_full_ellipse_fuselage = volume_payload_full_ellipse_fuselage / front_area_full_ellipse_fuselage

print(
    f'\nvolume utilization\n circle fuselage: {volume_utilization_cicrle_fuselage}\n ellipse fuselage: {volume_utilization_ellipse_fuselage}\n full ellipse: {volume_utilization_full_ellipse_fuselage}')

print(0.9 * volume_utilization_ellipse_fuselage)

l = 1000
thick = 1
diam = 100
volym = l * thick * pi * diam
densitet = 2.7 * 10 ** (-3)
massa = volym * densitet
print(massa)

'''BUDGET CALCUALTION'''
# number of people
SARC = 10
industry = 20
students = 25

people = SARC + industry + students

# costs per person
coffee = 25
fruit = 15
catering = 75
grill = 75
mingeltallrik = 25
cinnamon_bun = 12

total_costs_per_person = coffee + fruit + catering + grill + mingeltallrik + cinnamon_bun

# airfield
airfield = 15_000

total_budget = airfield + people * total_costs_per_person
print(f'total budget: {total_budget}')

print()
l_arm = 1.5  # cm

density = 1.225  # kg / m^3
speed = 30  # m/s
C_D = 1.28
A = 63 * 900 * 10 ** (-6)  # m^2
F_D = 1 / 2 * density * speed ** 2 * C_D * A  # N
T_D = F_D * l_arm / 9.82
print(T_D, 'kg cm')


def F_servo(C_D, density, speed, L, C, alpha_control, alpha_servo):
    T_servo = C_D * density * speed ** 2 * L * C ** 2 * np.sin(alpha_control) * np.tan(alpha_control) / (
                4 * np.tan(alpha_servo))
    return T_servo


deg_to_rad = pi / 180

alpha_control = 45 * deg_to_rad
alpha_servo = 60 * deg_to_rad
L = 0.9  # m
C = 0.06  # m

F_servo_max = F_servo(1, density, speed, L, C, alpha_control, alpha_servo)
F_servo_max_kgcm = F_servo_max / 0.098
print(f'{F_servo_max_kgcm:.2f}, kg cm')