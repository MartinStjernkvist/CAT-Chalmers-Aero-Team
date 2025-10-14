import numpy as np
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from mpl_toolkits import mplot3d

pi = np.pi
rho_air = 1.293  # kg / m^3

eta_static = 0.3
eta_cruise = 0.85


def T(eta, r, P):
    """
    :param eta: efficiency
    :param r: radius
    :param P: Power
    """
    return eta * np.sqrt(2 * rho_air * pi * r ** 2 * P ** 2)


def P(k, RPM, r, pitch):
    """
    :param k:
    :param RPM: rotations per minute
    :param r: radius
    :param pitch:
    """
    return k * RPM * (2 * r) ** 4 * pitch


D1 = 40
D2 = 2 * np.sqrt((1 / pi) * 4 * (D1 / 2) ** 2 * pi)
# print(D2)


amount = 50
base_price = 19.7  # kr, 80x80mm
special_thread = 1.15
all_thread = 1.15
postal = 79
student_discount = 0.9
total_price = amount * base_price * all_thread * student_discount + postal
print(f'\ntotal price: {total_price},\nprice per patch:{total_price / 50}')

"""
Half ellipse with cylinder payload vs Cirkel with square payload vs Ellipse with cylinder payload
"""
offset_wood = 15

diameter_circle_fuselage = 300
radius_circle_fuselage = diameter_circle_fuselage / 2
height_ellipse_fuselage = 350
width_ellipse_fuselage = 250

'''front area'''
# circle fuselage
front_area_circle_fuselage = pi * radius_circle_fuselage ** 2
print(f'front_area_circle_fuselage: {front_area_circle_fuselage}')

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
print(f'\nvolume_payload_circle_fuselage: {volume_payload_circle_fuselage}')

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

g = 9.82
max_massa = 15  # kg
oswald = 0.775  # mellan 0.7 och 0.85
parasitic_drag_rest = 2
C_L = 1.3

"""
functions
"""


def chord(A, AR):
    return np.sqrt(A / AR)


def span(A, AR):
    return np.sqrt(A * AR)


def RE(v, chord):
    return v * chord / (1.5 * 10 ** (-5))


def C_DI(C_L, AR):
    return C_L ** 2 / (np.pi * AR)


def F_DI(C_DI, v, A):
    # induced drag
    return C_DI * 1.225 * (v ** 2 / 2) * A


def L_D_airfoil_function(RE):
    return 52.983 * np.log(RE) - 573.67


def F_DI_RE_corr(L_D_value, F_DI, L_D):
    return L_D_value * (F_DI / L_D)


def L_D_RE_correction(L, parasitic_drag, F_DI_RE_corr):
    return L / (parasitic_drag + F_DI_RE_corr)


def L_D_no_corr(L, parasitic_drag, F_DI):
    return L / (parasitic_drag + F_DI)


def parasitic_drag(span, chord, speed):
    return span * chord * 0.16 * 0.01 * speed ** 2 * 1.29 / 2


"""
lists
"""

AR_list = np.linspace(12.5, 25, 100)

A = 0.78
A_list = [A] * len(AR_list)

L = max_massa * g / A  # N
L_list = [L] * len(AR_list)

v_list = np.linspace(12, 17, len(AR_list))

C_L_list = [C_L] * len(AR_list)

# chord_list = list(map(chord, AR_list, A_list))
# RE_list = list(map(RE, v_list, chord_list))
# span_list = list(map(span, A_list, AR_list))
# L_D_list = list(map(L_D_airfoil_function, RE_list))

'''---3D plot---'''
V, AR = np.meshgrid(v_list, AR_list)

chord = chord(A, AR)
RE = RE(V, chord)
print(RE)
L_D = L_D_airfoil_function(RE)

L_D_value = [L_D[0]] * len(AR_list)

C_DI = C_DI(C_L, AR)
F_DI = F_DI(C_DI, V, A)
F_DI_RE_corr = F_DI_RE_corr(L_D_value, F_DI, L_D)
L_D_RE_correction = L_D_RE_correction(L, parasitic_drag_rest, F_DI_RE_corr)

L_D_no_corr = L_D_no_corr(L, parasitic_drag_rest, F_DI)

"""
plotting
"""
big_font_size = 25
small_font_size = big_font_size * 0.75

fig = plt.figure(figsize=(10, 7.5))
ax = plt.axes(projection='3d')
ax.plot_surface(V, AR, L_D_RE_correction, rstride=1, cstride=1, cmap='binary', edgecolor='none', label='no correction')
# ax.contour3D(V, AR, L_D_no_corr, 100, cmap='viridis')
ax.plot_surface(V, AR, L_D_no_corr, rstride=1, cstride=1, cmap='viridis', edgecolor='none', label='corrected with RE')

ax.set_xlabel('V', fontsize=small_font_size)
ax.set_ylabel('AR', fontsize=small_font_size)
ax.set_zlabel('L/D', fontsize=small_font_size)

ax.set_zlim(0, 150)

plt.xticks(fontsize=small_font_size)
plt.yticks(fontsize=small_font_size)
plt.legend(fontsize=small_font_size)
plt.show()