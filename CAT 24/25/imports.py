# Genom att skriva "from imports import *" i nya filer kommer alla paket, konstanter och funktioner
# från denna fil att importeras till den nya filen.

import scipy.io
from matplotlib.widgets import Slider
from matplotlib.gridspec import GridSpec
import numpy as np
from numpy import random
import matplotlib.pyplot as plt
import time
import pandas as pd
from scipy.interpolate import interp1d
from numpy import random
from scipy.optimize import curve_fit
import multiprocessing as mp
import tkinter as tk
from tkinter import simpledialog
from numba import jit
import json

#   -----------------------------------
#   PLOTTNING
#   -----------------------------------

font_size = 20
font_size_title = font_size * 1.25
symbol_size = 150
line_width = 3

#   -----------------------------------
#   KONSTANTER
#   -----------------------------------

pi = np.pi
deg_to_rad = pi / 180

E_e = 0.511 * 10 ** 6  # eV
r_e = np.sqrt(0.07941)  # sqrt(b): re2 = e4/Ee2 ≈ 0.07941 b, https://en.wikipedia.org/wiki/Gamma_ray_cross_section
a_0 = 5.29177210903 * 10 ** (-11) * 10 ** 14  # sqrt(b), bohr radius of hydrogen
c = 3 * 10 ** 8

r_e_m = 2.81 * 10 ** (-15)  # Elektronradie i meter.

radie_alpha = 1.2 * 10 ** (-15) * 4 ** (1 / 3)  # Radie alfapartikel i meter (Physics Handbook)

rho_vatten = 998  # Vattens densitet i kg / m^3.

#   -----------------------------------
#   Funktioner
#   -----------------------------------

def plot_stuff(x_data, y_data, scatter, label_data,
               marker='o', color='blue', x_label='x-label', y_label='y-label', title='1',
               fig_size=(10, 10), symbol_size=100, font_size=30, alpha=1, line_width=10, x_lim=(0, 0), y_lim=(0, 0),
               grid=False, x_scale='linear', y_scale='linear'):
    """
    Funktion som skapar 2D plottar. Används nog inte i koden.
    """
    fig = plt.figure(figsize=fig_size)

    if x_lim != (0, 0) and y_lim != (0, 0):
        plt.ylim(y_lim)
        plt.xlim(x_lim)

    if grid == True:
        plt.grid()

    if scatter == 0:
        plt.plot(x_data, y_data, color=color, alpha=alpha, linewidth=line_width, label=label_data)
    elif scatter == 1:
        plt.scatter(x_data, y_data, marker=marker, color=color, alpha=alpha, s=symbol_size, label=label_data)
    elif scatter == 2:
        plt.plot(x_data, y_data, color=color, alpha=alpha, linewidth=line_width, label=label_data)
        plt.scatter(x_data, y_data, marker=marker, color=color, alpha=alpha, s=symbol_size, label=label_data)
    else:
        for i in range(len(x_data)):
            if scatter[i] == 1:
                plt.scatter(x_data[i], y_data[i], marker=marker[i], color=color[i],
                            alpha=alpha, s=symbol_size, label=label_data[i])
            else:
                plt.plot(x_data[i], y_data[i], color=color[i], alpha=alpha, linewidth=line_width, label=label_data[i])

    font_size_ticks = font_size * 0.85

    plt.xscale(x_scale)
    plt.yscale(y_scale)

    plt.xlabel(x_label, fontsize=font_size)
    plt.ylabel(y_label, fontsize=font_size)

    plt.xticks(fontsize=font_size_ticks)
    plt.yticks(fontsize=font_size_ticks)

    plt.title(title, fontsize=font_size)
    plt.legend(fontsize=font_size_ticks)

    return fig


def end_time(start):
    """
    Funktion som tar tiden för hur lång tid beräkningarna tar.
    """
    end = time.time()
    runtime = round((end - start), 1)
    if runtime < 60:
        print(f'Runtime: {runtime} seconds')
    else:
        print('Runtime: ' + str(round((runtime / 60), 1)) + ' minutes')


