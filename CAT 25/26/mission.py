#%%
# Interactive python file (can be viewed within vscode interactive python window)

# Imports
import numpy as np
import matplotlib.pyplot as plt
from sympy import *
import math
import pandas as pd

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

from pathlib import Path

# Plotting
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
    
def fig(fig_name):
    fig_output_file = script_dir / "fig" / fig_name
    fig_output_file.parent.mkdir(parents=True, exist_ok=True)
    plt.legend()
    plt.grid(True, alpha = 0.3)
    plt.savefig(fig_output_file, dpi=dpi, bbox_inches='tight')
    plt.show()


#%%