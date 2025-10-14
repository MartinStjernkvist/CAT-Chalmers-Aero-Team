from imports import *


def T_servo(alpha_servo, C_D, density, speed, L, C, alpha_control):
    T_servo = C_D * density * speed ** 2 * L * C ** 2 * np.sin(alpha_control) * np.tan(alpha_control) / (
            4 * np.tan(alpha_servo))
    return T_servo


l_arm = 1.5  # cm

L = 1.3  # m
# C = 0.06  # m
# C = 0.086
C = 0.09

density = 1.225  # kg / m^3
speed = 30  # m/s
C_D = 1.28
A = C * L  # m^2
F_D = 1 / 2 * density * speed ** 2 * C_D * A  # N
T_D = F_D * l_arm / 9.82
print(T_D, 'kg cm')

deg_to_rad = pi / 180

alpha_control = 45 * deg_to_rad
alpha_servo = 60 * deg_to_rad

F_servo_max = T_servo(alpha_servo, 1, density, speed, L, C, alpha_control)
F_servo_max_kgcm = F_servo_max / 0.098
print(f'{F_servo_max_kgcm:.2f}, kg cm')

vinklar_linspace = np.linspace(5 * deg_to_rad, 45 * deg_to_rad, 1000)

"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
PLOTTNING
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

deflection = np.arange(1, 55, 5)
C_D_min = 0.1
C_D_max = 1.2

params = []
T_list = []
for i in range(len(deflection)):
    C_D = C_D_min + C_D_max * (deflection[i] - deflection[0]) * ((C_D_max - C_D_min) / (deflection[-1] - deflection[0]))
    params_instance = C_D, density, speed, L, C, deflection[i] * deg_to_rad
    params.append([params_instance])
    T_list.append(T_servo(vinklar_linspace, *params_instance))

x_data = [[i / deg_to_rad for i in vinklar_linspace] for i in range(len(deflection))]
y_data = T_list

import matplotlib as mpl

n_lines = len(deflection)
cmap = mpl.colormaps['plasma']
colors = cmap(np.linspace(0, 1, len(deflection)))

scatter = [0 for i in range(len(deflection))]
label_data = [deflection[i] for i in range(len(deflection))]
marker = ['X' for i in range(len(deflection))]
color = [colors[i] for i in range(len(deflection))]

x_label = 'deflection servo (degrees)'
y_label = 'torque (kg * cm)'
title = f'deflection control surface'

fig = plot_stuff(x_data, y_data, scatter, label_data,
                 marker, color, x_label, y_label, title,
                 fig_size=(10, 10), symbol_size=symbol_size, font_size=font_size, alpha=1, line_width=line_width,
                 x_lim=(1, 45),
                 y_lim=(0, 12),
                 grid=True, x_scale='linear', y_scale='linear')

fig.savefig(title, bbox_inches='tight')

print((1/(np.sqrt(2)) - 4/3 * np.cos(np.pi / 3))**2)
print((-1/np.sqrt(2) + 4/3 * np.sin(pi/3))**2)
print(((1/(np.sqrt(2)) - 4/3 * np.cos(np.pi / 3))**2 + (-1/np.sqrt(2) + 4/3 * np.sin(pi/3))**2)*9)