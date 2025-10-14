import numpy as np
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def Cl_Cd(alpha=False, Cl_max=False, Cl=False):
    # NACA 2412
    alpha_ref = np.array([-5, 0, 5, 10, 15, 20])
    Cl_ref = np.array([-0.3, 0.25, 0.8, 1.25, 1.45, 1.3])
    Cd_ref = np.array([0.01, 0.008, 0.01, 0.02, 0.05, 0.13])

    if Cl_max:
        Cl = np.max(Cl_ref)
        Cd = Cd_ref[Cl == Cl_ref]
    elif Cl is not False:
        Cd = np.interp(Cl, Cl_ref, Cd_ref)
        return Cd
    elif alpha is not False:
        Cl = np.interp(alpha, alpha_ref, Cl_ref)
        Cd = np.interp(alpha, alpha_ref, Cd_ref)
    else:
        print("Wrong input for Cl_Cd, returning dummy values")
        return np.mean(Cl_ref), np.mean(Cd_ref)

    return Cl, Cd


def PT_mass(P_max):
    # Ref engine
    V = 12
    A = 60
    P = V * A
    W = 0.120
    W_P = W / P

    return W_P * P_max


def S_mass(S_wet):
    # Weight per surface area, guessed 1.3 kg/m^2
    return S_wet * 1.3


def PT_T(P, V):
    return P * PT_eta(P, V) / V


def PT_eta(P, V):
    # Power train efficiency, fixed at 85% until better function
    return 0.85


def Calc_score(Performance):
    Weighting_factors = np.array([-4, 7, 25, 4, -4, 5, -3, 8, -12, 10, 18])
    scores = Weighting_factors * Performance

    return [np.sum(scores), scores]


# ----- Input
M_TO = 15
M_bat = 3
rho = 1.12

# Energy storage in Wh, assuming 260 Wh/kg and 3 kg of batteries
E_total = 260 * 3

# Needs a better estimation of Cd_fuse!!! Scaled with fuselage surface area
Cd_fuse = 0.02

# ----- Optim
V_Endurance = 15  # m/s
P_max = 600  # Watt
S_wing = 2  # m^2
S_fuse = 1  # m^2

# ----- Calc
# ----- TO
# Integration time step
dt = 0.01
V_TO = np.array([1])
Cl_max, Cd_TO = Cl_Cd(Cl_max=True)
V_TO_lim = (2 * M_TO * 9.82 / (Cl_max * rho * S_wing)) ** 0.5
while V_TO[-1] < V_TO_lim:
    D_TO = 0.5 * Cd_TO * rho * V_TO[-1] ** 2 * (S_fuse + S_wing)
    a_TO = (P_max / V_TO[-1] - D_TO) / M_TO
    V_TO = np.append(V_TO, V_TO[-1] + a_TO * dt)

d_TO = np.cumsum(V_TO * dt)
E_TO = np.sum(P_max * dt * np.ones_like(d_TO)) / 3600  # Wh

plt.figure()
plt.plot(d_TO, V_TO)
plt.scatter(d_TO, V_TO)
plt.title("Take off")
plt.ylabel('Velocity [m/s]')
plt.xlabel('Distance [m]')

# ------ Climb
# Starting from end of runway speed and accelerating
# Assume we're still flying at Cl_max and P_max
# Cordinate system
# - V_toAir is along the climb angle
# - Cl, L is orthogonal to thrust and Cd, D is parallel to thrust
# - Assuming that vertical drag is very low
# Integration time step
dt = 0.01
V_Climb_toAir = np.array([V_TO_lim])
angle_Climb = np.array([0])
Altitude = np.array([0])
Cl_max, Cd_Climb = Cl_Cd(Cl_max=True)
while Altitude[-1] < 100:
    # for i in range(100):
    # 	angle_Climb = np.arctan(V_Climb_vertical[-1]/V_Climb_horisontal[-1])
    # 	V_Climb_toAir = np.sqrt(V_Climb_horisontal[-1]**2+V_Climb_vertical[-1]**2)
    L_Climb = 0.5 * Cl_max * rho * V_Climb_toAir[-1] ** 2 * (S_wing)
    D_Climb = 0.5 * Cd_Climb * rho * V_Climb_toAir[-1] ** 2 * (S_fuse + S_wing)

    T_Climb = PT_T(P_max, V_Climb_toAir[-1])  # Simplified!!!

    T_excess = T_Climb - D_Climb - M_TO * 9.82 * np.sin(angle_Climb[-1])

    V_Climb_toAir = np.append(V_Climb_toAir, V_Climb_toAir[-1] + T_excess / (M_TO) * dt)

    Force_sum_vertical = T_Climb * np.sin(angle_Climb[-1]) + L_Climb * np.cos(angle_Climb[-1]) - D_Climb * np.sin(
        angle_Climb[-1]) - 9.82 * M_TO
    Force_sum_horisontal = T_Climb * np.cos(angle_Climb[-1]) - D_Climb * np.cos(angle_Climb[-1]) - L_Climb * np.sin(
        angle_Climb[-1])

    a_CLimb_vertical = Force_sum_vertical / M_TO
    V_Climb_vertical = V_Climb_toAir[-1] * np.sin(angle_Climb[-1]) + a_CLimb_vertical * dt

    a_CLimb_horisontal = Force_sum_horisontal / M_TO
    V_Climb_horisontal = V_Climb_toAir[-1] * np.cos(angle_Climb[-1]) + a_CLimb_horisontal * dt

    # For some reason it oscillates a lot... removing 1% from the new climb angle helped a lot...???
    angle_Climb = np.append(angle_Climb, 0.997 * np.arctan(V_Climb_vertical / V_Climb_horisontal))

    Altitude = np.append(Altitude, Altitude[-1] + V_Climb_vertical * dt)
# print(Altitude[-1])

d_Climb_horisontal = np.cumsum(V_Climb_toAir * np.cos(angle_Climb) * dt)
E_Climb = np.sum(P_max * dt * np.ones_like(d_Climb_horisontal)) / 3600  # Wh

plt.figure()
plt.plot(d_Climb_horisontal, Altitude)
plt.scatter(d_Climb_horisontal, Altitude)
plt.title("Climb")
plt.ylabel('Altitude [m]')
plt.xlabel('Distance [m]')

# Whatever energy is left
E_Endurance = 1
# ----- Endurance
# Only sing contributing to lift
Cl_Endurance = M_TO * 9.82 / (0.5 * rho * V_Endurance ** 2 * (S_wing))
# Wing and fuse contributing to drag, should get a Cd_fuse!
D_Endurance = 0.5 * Cl_Cd(Cl=Cl_Endurance) * rho * V_TO[-1] ** 2 * (S_fuse + S_wing)
P_Endurance = D_Endurance * V_Endurance
t_Endurance = E_Endurance / (P_Endurance / PT_eta(D_Endurance, V_Endurance) * D_Endurance / 3600)

# Glide ratio
alpha_GR = np.linspace(0, 15)
Cl_GR, Cd_GR = Cl_Cd(alpha=alpha_GR)

Glide_ratio = np.max(Cl_GR * S_wing / (Cd_GR * S_wing + Cd_fuse * S_fuse))
alpha_glide = alpha_GR[Glide_ratio == Cl_GR * S_wing / (Cd_GR * S_wing + Cd_fuse * S_fuse)]
Cl_glide = Cl_GR[Glide_ratio == Cl_GR * S_wing / (Cd_GR * S_wing + Cd_fuse * S_fuse)]

V_glide = (2 * M_TO * 9.82 / (Cl_glide * rho * S_wing)) ** 0.5

# Summing up
E_total = E_TO + E_Climb + E_Endurance

# Payload
# Payload mass is whatever is left! Needs to subtract more
Mass_payload = M_TO - S_mass(S_wing + S_fuse) - M_bat

# Payload volume from surface area, diameter and utilization ratio
Dia_fuse = 0.35
# Assuming a perfect cylinder
Length_fuse = S_fuse / (2 * np.pi * Dia_fuse / 2)
Volume_fuse = (Dia_fuse) ** 2 * np.pi * Length_fuse
Volume_payload = 0.61 * Volume_fuse

Performance = np.array(
    [D_TO, np.mean(angle_Climb), Glide_ratio, speed_max, speed_min, np.mean(angle_Landing), D_landing, D_Endurance,
     EC_specific, Mass_payload, Volume_payload])
