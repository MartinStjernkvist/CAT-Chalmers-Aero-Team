import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import minimize
from scipy.interpolate import LinearNDInterpolator

# =====================
# CONSTANTS
# =====================
g = 9.81
rho0 = 1.225

# =====================
# BATTERY
# =====================
class Battery:
    def __init__(self, capacity_Ah, V_nom, R_internal):
        self.capacity_As = capacity_Ah * 3600
        self.V_nom = V_nom
        self.R = R_internal
        self.soc = 1.0

    def voltage(self, I):
        return max(self.V_nom * self.soc - I * self.R, 0.0)

    def update(self, I, dt):
        self.soc -= (I * dt) / self.capacity_As
        self.soc = max(self.soc, 0.0)

# =====================
# ESC
# =====================
class ESC:
    def __init__(self, I_max):
        self.I_max = I_max

    def limit(self, I):
        return min(I, self.I_max)

# =====================
# MOTOR
# =====================
class Motor:
    def __init__(self, Kv, R, I_max, P_max):
        self.Kv = Kv
        self.R = R
        self.I_max = I_max
        self.P_max = P_max
        self.Kt = 60 / (2 * np.pi * Kv)

    def torque_current(self, V_batt, omega):
        V_emf = omega * (60 / (2*np.pi)) / self.Kv
        I = max((V_batt - V_emf) / self.R, 0.0)
        I = min(I, self.I_max)
        Q = self.Kt * I
        P = Q * omega
        if P > self.P_max:
            Q = self.P_max / omega
            P = self.P_max
        return Q, I, P

# =====================
# PROPELLER, 0 alpha approximation
# =====================
class Propeller: # Everything you need: https://m-selig.ae.illinois.edu/props/propDB.html
    def __init__(self, D, CT_func, CQ_func):
        self.D = D
        self.CT = CT_func
        self.CQ = CQ_func

    def forces(self, V, omega, rho):
        n = omega / (2*np.pi)
        J = V / (n * self.D + 1e-6)
        T = self.CT(J) * rho * n**2 * self.D**4
        Q = self.CQ(J) * rho * n**2 * self.D**5
        return T, Q

# =====================
# AIRCRAFT
# =====================
class Aircraft:
    def __init__(self, mass, S, CL_func, CD_func, mu_roll):
        self.mass = mass
        self.S = S
        self.CL = CL_func
        self.CD = CD_func
        self.mu = mu_roll

    def lift(self, V, alpha):
        return 0.5 * rho0 * V**2 * self.S * self.CL(alpha)

    def drag(self, V, alpha):
        return 0.5 * rho0 * V**2 * self.S * self.CD(alpha)

# =====================
# SIMULATOR
# =====================
class MissionSimulator:
    def __init__(self, aircraft, motor, esc, prop, battery):
        self.ac = aircraft
        self.motor = motor
        self.esc = esc
        self.prop = prop
        self.batt = battery

    def solve_motor_prop(self, V, full_power):
        omegas = np.linspace(300, 12000 * 2*np.pi/60, 250)
        best, err_min = None, 1e9

        for omega in omegas:
            Vb = self.batt.voltage(0)
            Qm, I, P = self.motor.torque_current(Vb, omega)
            I = self.esc.limit(I)
            Qm = self.motor.Kt * I

            if full_power:
                P = min(P, self.motor.P_max)
                Qm = P / omega

            T, Qp = self.prop.forces(V, omega, rho0)
            err = abs(Qm - Qp)

            if err < err_min:
                err_min = err
                best = (omega, T, I, P)

        return best

    # =====================
    # TAKEOFF
    # =====================
    def simulate_takeoff(self, dt, alpha_TO):
        V, x, t = 0.1, 0.0, 0.0
        W = self.ac.mass * g
        hist = []

        while True:
            L = self.ac.lift(V, alpha_TO)
            D = self.ac.drag(V, 2)
            omega, T, I, P = self.solve_motor_prop(V, full_power=True)

            F_roll = self.ac.mu * max(W - L, 0)
            a = (T - D - F_roll) / self.ac.mass

            print("Velocity", V, "Lift/Weight", L/W)
            if a * dt / V < 0.00001:
                print("No longer accelerating, take-off failed, increase max thrust!")
                break
            V += a * dt
            x += V * dt
            t += dt
            self.batt.update(I, dt)

            hist.append(dict(
                t=t, h=0.0, x=x, V=V, alpha=alpha_TO,
                T=T, P=P, soc=self.batt.soc
            ))

            if L >= W:
                break

        return hist

    # =====================
    # CLIMB (Steady state at max throttle, provide alpha, solve for V and gamma)
    # =====================
    def simulate_climb_steady(self, h_target, T0, alpha_climb):
        # Initiate velocity, altitude, distance and time
        h, x, t = 0.0, 0.0, T0
        # Weight to carry
        W = self.ac.mass * g
        hist = []

        def force_equilibrium(x):
            gamma, V = x
            # Calculate lift
            L = self.ac.lift(V, alpha_climb)
            # Calculate drag
            D = self.ac.drag(V, alpha_climb)

            # Solve motor and prop at that speed, full throttle assumed
            omega, T, I, P = self.solve_motor_prop(V, full_power=True)

            # 2D Force equilibrium
            # Vertical
            i1 = L*np.cos(np.deg2rad(gamma))+T*np.sin(np.deg2rad(gamma+alpha_climb))-D*np.sin(np.deg2rad(gamma))-W

            # Horisontal
            i2 = T*np.cos(np.deg2rad(gamma+alpha_climb))-L*np.sin(np.deg2rad(gamma))-D*np.cos(np.deg2rad(gamma))

            return np.abs(i1)+np.abs(i2)

        x0 = [5, 20]
        bounds = [(1, 70), (10, 35)]

        res = minimize(force_equilibrium, x0, bounds=bounds, method="Powell")

        gamma, V = res.x

        print(r"Climb $\gamma$ : ", gamma, r" Climb V : ", V)

        # Solve motor and prop at that speed, full throttle assumed
        omega, T, I, P = self.solve_motor_prop(V, full_power=True)

        h += h_target
        x += h_target/np.tan(np.deg2rad(gamma))
        t += np.sqrt(h_target**2+(h_target/np.tan(np.deg2rad(gamma)))**2)/V
        self.batt.update(I, t)

        hist.append(dict(
            t=t, h=h, x=x, V=V, alpha=alpha_climb,
            T=t, P=P, soc=self.batt.soc
        ))

        print("Time to climb : ",np.sqrt(h_target**2+(h_target/np.tan(np.deg2rad(gamma)))**2)/V)

        return hist
    def simulate_climb(self, dt, h_target, V0, T0):
        # Initiate velocity, altitude, distance and time
        V, h, x, t = V0, 0.0, 0.0, T0
        # Weight to carry
        W = self.ac.mass * g
        hist = []

        # While below target altitude
        while h < h_target:
            # Solve alpha from lift = weight (small gamma assumption)
            alphas = np.linspace(-3, 15, 200) * np.pi/180
            Ls = [self.ac.lift(V, a) for a in alphas]
            alpha = alphas[np.argmin(np.abs(np.array(Ls) - W))]

            # Calculate associated drag
            D = self.ac.drag(V, alpha)

            # Solve motor and prop at that speed, full throttle assumed
            omega, T, I, P = self.solve_motor_prop(V, full_power=True)

            # Energy method
            P_excess = max(T*V - D*V, 0.0)
            h_dot = P_excess / W

            # Velocity dynamics (small longitudinal accel)
            a = (T - D) / self.ac.mass

            V += a * dt
            h += h_dot * dt
            x += V * dt
            t += dt
            self.batt.update(I, dt)

            hist.append(dict(
                t=t, h=h, x=x, V=V, alpha=alpha,
                T=T, P=P, soc=self.batt.soc
            ))

            print(h/h_target)

        return hist

    # =====================
    # Cruise (Steady state at given alpha)
    # # =====================
    def simulate_cruise(self, T0, h0, cruise_d, V_cruise):
        # Initiate velocity, altitude, distance and time
        h, x, t = h0, 0, T0
        # Weight to carry
        W = self.ac.mass * g
        hist = []

        def force_equilibrium(x):
            alpha = x
            # Calculate lift
            L = self.ac.lift(V_cruise, alpha)
            # Calculate drag
            D = self.ac.drag(V_cruise, alpha)

            # Solve motor and prop at that speed, full throttle assumed
            omega, T, I, P = self.solve_motor_prop(V_cruise, full_power=True)

            # 2D Force equilibrium
            # Vertical
            i1 = L - W

            # Horisontal
            i2 = T * np.cos(np.deg2rad(alpha)) - D

            return np.abs(i1) + np.abs(i2)

        x0 = [5]
        bounds = [(1, 13)]

        res = minimize(force_equilibrium, x0, bounds=bounds, method="Powell")

        alpha = res.x

        print(r"Cruise $\alpha$ : ", alpha)

        # Solve motor and prop at that speed, full throttle assumed
        omega, T, I, P = self.solve_motor_prop(V_cruise)# , full_power=True)

        h = np.append(h,h0)
        x = np.append(x,x[-1]+cruise_d)
        t += cruise_d/V_cruise
        self.batt.update(I, t)

        hist.append(dict(
            t=t, h=h, x=x, V=V_cruise, alpha=alpha[0],
            T=t, P=P, soc=self.batt.soc
        ))

        # print("Time to climb : ", np.sqrt(h_target ** 2 + (h_target / np.tan(np.deg2rad(gamma))) ** 2) / V)
        return hist

# =====================
# AERO & PROP CURVES
# =====================
def CL(alpha): # From CFD results extracted 2026-01-15
    # alpha array (deg)
    alpha_deg = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    # corresponding CL values
    CL_data = np.array([0.517, 0.617, 0.727, 0.793, 0.866, 0.964, 1.016, 1.104, 1.164, 1.228, 1.296, 1.386, 1.455])

    return interp1d(alpha_deg, CL_data, kind='quadratic', fill_value='extrapolate')(alpha)

def CD(alpha): # From CFD results extracted 2026-01-15
    # alpha array (deg)
    alpha_deg = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

    # corresponding CD values
    CD_data = np.array([0.059, 0.063, 0.070, 0.075, 0.081, 0.090, 0.098, 0.109, 0.118, 0.129, 0.140, 0.154, 0.166])

    return interp1d(alpha_deg, CD_data, kind='quadratic', fill_value='extrapolate')(alpha)

def CT(J): # Currently for the apce_19x12 at 2500 RPM, https://m-selig.ae.illinois.edu/props/volume-1/propDB-volume-1.html
    # advance ratio
    J_data = np.array([0.185, 0.210, 0.245, 0.276, 0.306, 0.335, 0.364, 0.399, 0.429, 0.456, 0.481, 0.521, 0.545, 0.576, 0.600, 0.603, 0.642, 0.664, 0.695, 0.723, 0.756])

    # corresponding CT values
    CT_data = np.array([0.0893, 0.0875, 0.0852, 0.0826, 0.0797, 0.0768, 0.0737, 0.0691, 0.0648, 0.0601, 0.0550, 0.0448, 0.0397, 0.0401, 0.0322, 0.0273, 0.0201, 0.0163, 0.0108, 0.0058, -0.0005])

    return interp1d(J_data, CT_data, kind='quadratic', fill_value='extrapolate')(J)

def CQ(J): # Currently for the apce_19x12 at 2500 RPM, https://m-selig.ae.illinois.edu/props/volume-1/propDB-volume-1.html
    # advance ratio
    J_data = np.array([0.185, 0.210, 0.245, 0.276, 0.306, 0.335, 0.364, 0.399, 0.429, 0.456, 0.481, 0.521, 0.545, 0.576, 0.600, 0.603, 0.642, 0.664, 0.695, 0.723, 0.756])

    # corresponding CT values
    CP_data = np.array([0.0412, 0.0414, 0.0419, 0.0420, 0.0420, 0.0419, 0.0418, 0.0411, 0.0403, 0.0390, 0.0373, 0.0331, 0.0307, 0.0267, 0.0245, 0.0242, 0.0205, 0.0185, 0.0154, 0.0126, 0.0089])

    CQ_data = CP_data / (2 * np.pi)

    return interp1d(J_data, CQ_data, kind='quadratic', fill_value='extrapolate')(J)

# =====================
# VEHICLE DEFINITION
# =====================
aircraft = Aircraft(
    mass=10.0,      # Take-off mass
    S=0.9,          # Wing ref area (top surface area)
    CL_func=CL,     # Lift coefficient curve
    CD_func=CD,     # Drag coefficient curve
    mu_roll=0.03    # Rolling resistance (could be removed)
)

battery = Battery(
    capacity_Ah=6,  # Capacity
    V_nom=22.2,     # Voltage
    R_internal=0.03 # Internal resistance
)

esc = ESC(I_max=60) # ESC max current

motor = Motor(
    Kv=380,         # RPM/Volt value
    R=0.05,         # Internal resistance
    I_max=75,       # Max current
    P_max=1800      # Max power
)

prop = Propeller(
    D=0.48,         # Diameter [m]
    CT_func=CT,     # Thrust coefficient curve
    CQ_func=CQ      # Torque coefficient curve
)

sim = MissionSimulator(aircraft, motor, esc, prop, battery)

# =====================
# RUN MISSION
# =====================
print("Starting sim")
takeoff = sim.simulate_takeoff(dt=0.02, alpha_TO=10)
print("Take-off done")
# climb = sim.simulate_climb(h_target=120, V=takeoff[-1]["V"], T0=takeoff[-1]["t"])
#climb = sim.simulate_climb_steady(h_target=120, T0=takeoff[-1]["t"], alpha_climb=10)
print("Climb done")
#cruise = sim.simulate_cruise(T0=climb[-1]["t"], h0=120, cruise_d=1000, V_cruise=15)
print("Cruise done")

mission = takeoff #+ climb + cruise

# =====================
# PLOTTING
# =====================
t     = np.array([r["t"] for r in mission])
h     = np.array([r["h"] for r in mission])
x     = np.array([r["x"] for r in mission])
V     = np.array([r["V"] for r in mission])
T     = np.array([r["T"] for r in mission])
P     = np.array([r["P"] for r in mission])
soc   = np.array([r["soc"] for r in mission])
alpha = np.array([r["alpha"] for r in mission])

plots = [
    (h, "Altitude [m]"),
    (x, "Distance [m]"),
    (V, "Velocity [m/s]"),
    (T, "Thrust [N]"),
    (P, "Power [W]"),
    (soc, "SOC [-]"),
    (alpha, "Angle of Attack [deg]")
]

for y, label in plots:
    plt.figure()
    plt.plot(t, y)
    plt.xlabel("Time [s]")
    plt.ylabel(label)
    plt.grid()
    plt.show()
