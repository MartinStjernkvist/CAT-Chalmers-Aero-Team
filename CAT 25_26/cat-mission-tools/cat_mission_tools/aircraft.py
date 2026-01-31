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

from cat_mission_tools.utils import rho0


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
