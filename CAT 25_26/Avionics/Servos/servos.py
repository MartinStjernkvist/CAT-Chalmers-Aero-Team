import numpy as np
import math
import sympy as sp

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from IPython.display import display, Math
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d import Axes3D
from numpy.random import rand
from IPython.display import HTML
from matplotlib import animation
import scipy.io as sio
from scipy.optimize import fsolve
from matplotlib import rcParams # for changing default values
import matplotlib.ticker as ticker

import calfem.core as cfc
import calfem.vis_mpl as cfv
import calfem.mesh as cfm
import calfem.utils as cfu

from scipy.sparse import coo_matrix, csr_matrix
import matplotlib.cm as cm

from pathlib import Path

SMALL_SIZE = 10
MEDIUM_SIZE = 12
BIGGER_SIZE = 14
dpi = 500

# Set the global font sizes
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
plt.rc('figure', figsize=(8,4))

script_dir = Path(__file__).parent

def sfig(fig_name):
    fig_output_file = script_dir / "figures" / fig_name
    fig_output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(fig_output_file, dpi=dpi, bbox_inches='tight')
    
def fig(fig_name):
    '''
    standard matplotlib commands
    '''
    plt.legend()
    plt.grid(True, alpha = 0.3)
    sfig(fig_name)
    plt.show()
    print('figure name: ', fig_name)





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

deg_to_rad = np.pi / 180.0

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

x_label = 'deflection servo (degrees)'
y_label = 'torque (kg * cm)'
title = f'deflection control surface'

plt.figure()
plt.xlim(1, 45)
plt.ylim(0, 12)
plt.ylabel(y_label)
plt.xlabel(x_label)
    
for i in range(len(deflection)):
    C_D = C_D_min + C_D_max * (deflection[i] - deflection[0]) * ((C_D_max - C_D_min) / (deflection[-1] - deflection[0]))
    params_instance = C_D, density, speed, L, C, deflection[i] * deg_to_rad
    params.append([params_instance])
    T_list.append(T_servo(vinklar_linspace, *params_instance))
    x_data = [i / deg_to_rad for i in vinklar_linspace]

    plt.plot(x_data, T_servo(vinklar_linspace, *params_instance), label=fr'angle: {deflection[i]}*')

fig(title)

print((1/(np.sqrt(2)) - 4/3 * np.cos(np.pi / 3))**2)
print((-1/np.sqrt(2) + 4/3 * np.sin(np.pi/3))**2)
print(((1/(np.sqrt(2)) - 4/3 * np.cos(np.pi / 3))**2 + (-1/np.sqrt(2) + 4/3 * np.sin(np.pi/3))**2)*9)