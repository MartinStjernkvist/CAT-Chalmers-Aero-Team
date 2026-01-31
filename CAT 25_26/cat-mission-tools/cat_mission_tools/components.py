# This code is part of the CAT mission tools
#
# (C) Copyright Chalmers Aero Team 2026
# (C) Copyright Petter Miltén 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import numpy as np

from cat_mission_tools.utils import rpm_to_rads


class Battery:
    def __init__(self, capacity_Ah, V_nom, R_internal):
        self.capacity_As = capacity_Ah * 3600
        self.V_nom = V_nom
        self.R = R_internal
        self.soc = 1.0

    def voltage(self, I):
        return max(self.V_nom * self.soc - I * self.R, 0.0)

    def update(self, I, dt):
        soc_ = self.soc - ((I * dt) / self.capacity_As)
        self.soc = min(max(soc_, 0.0), 1.0)


class ESC:
    def __init__(self, I_max):
        self.I_max = I_max

    def limit(self, I):
        return min(I, self.I_max)


class Motor:
    def __init__(self, Kv, R, I_max, P_max):
        self.Kv = Kv
        self.R = R
        self.I_max = I_max
        self.P_max = P_max
        self.Kt = 60 / (2 * np.pi * Kv)

    def torque_current(self, V_batt, omega):
        # Input validation
        if V_batt < 0 or omega < 0:
            raise ValueError("V_batt and omega must be non-negative.")

        V_emf = omega * rpm_to_rads / self.Kv

        # Calculate current with limits
        I = max((V_batt - V_emf) / self.R, 0.0)
        I = min(I, self.I_max)

        # Calculate torque and power
        Q = self.Kt * I
        P = Q * omega

        # Handle division by zero for omega = 0
        if omega == 0:
            P = 0.0
            Q = 0.0
        else:
            # Enforce power limit
            if P > self.P_max:
                Q = self.P_max / omega
                P = self.P_max

        return Q, I, P

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
