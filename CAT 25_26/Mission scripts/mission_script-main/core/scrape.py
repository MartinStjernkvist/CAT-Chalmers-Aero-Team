import os
import re
import numpy as np
import pandas as pd
import xlrd


def file_speed(filename):
    match = re.search(r"(\d+[.,_]\d+)\s*m[_ ]s", filename)
    if not match:
        return None

    number = match.group(1).replace("_", ".")
    return float(number)


def load_file(path):
    alphas, cls, cds = [], [], []
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                a = float(parts[0])
                Cl = float(parts[2])
                Cd = float(parts[5])
                alphas.append(a)
                cls.append(Cl)
                cds.append(Cd)
            except ValueError:
                continue
    return np.array(alphas), np.array(cls), np.array(cds)


def get_cl_cd(speed, alpha, folder):
    folder = os.getcwd() + "/" + folder
    if not os.path.isdir(folder):
        raise RuntimeError(f"Folder not found: {folder}")
    files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    speed_map = {}
    for f in files:
        s = file_speed(f)
        if s is not None:
            speed_map[f] = s

    if not speed_map:
        raise RuntimeError("No valid speed-encoded files found.")

    # snap to closest speed
    best_file = min(speed_map, key=lambda fn: abs(speed_map[fn] - speed))
    best_speed = speed_map[best_file]

    path = os.path.join(folder, best_file)
    alphas, cls, cds = load_file(path)

    if len(alphas) == 0:
        raise RuntimeError(f"No aerodynamic data found in: {path}")

    cl = np.interp(alpha, alphas, cls)
    cd = np.interp(alpha, alphas, cds)

    return cl, cd, best_speed, best_file
