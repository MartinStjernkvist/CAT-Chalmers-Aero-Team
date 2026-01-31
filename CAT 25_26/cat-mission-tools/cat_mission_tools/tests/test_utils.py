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

from cat_mission_tools.utils import g, rho0


def test_constants():
    assert g == 9.81
    assert rho0 == 1.225