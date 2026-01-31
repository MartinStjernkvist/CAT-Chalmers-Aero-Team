# This code is part of the CAT mission tools
#
# (C) Copyright Chalmers Aero Team 2026
# (C) Copyright Stefan Hill 2026
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import pytest

import numpy as np

from cat_mission_tools.components import Battery, ESC, Motor


def test_battery_initialization():
    battery = Battery(capacity_Ah=10, V_nom=12, R_internal=0.1)
    assert battery.capacity_As == 10 * 3600
    assert battery.V_nom == 12
    assert battery.R == 0.1
    assert battery.soc == 1.0

def test_battery_voltage():
    battery = Battery(capacity_Ah=10, V_nom=12, R_internal=0.1)
    assert battery.voltage(I=0) == 12
    assert battery.voltage(I=5) == max(12 - 5 * 0.1, 0.0)
    assert battery.voltage(I=200) == 0.0  # High current should result in 0 voltage

def test_battery_update():
    battery = Battery(capacity_Ah=10, V_nom=12, R_internal=0.1)
    battery.update(I=5, dt=10)
    assert battery.soc == max(1.0 - (5 * 10) / (10 * 3600), 0.0)

def test_battery_update_negative_current():
    battery = Battery(capacity_Ah=10, V_nom=12, R_internal=0.1)
    battery.soc = 0.5  # Set SOC to 50%
    battery.update(I=-5, dt=10)  # Negative current (charging)
    assert battery.soc == min(0.5 + (5 * 10) / (10 * 3600), 1.0)

def test_battery_soc_limits():
    battery = Battery(capacity_Ah=10, V_nom=12, R_internal=0.1)
    battery.soc = 0.0
    battery.update(I=5, dt=10)
    assert battery.soc == 0.0  # SOC should not go below 0

    battery.soc = 1.0
    battery.update(I=-5, dt=10000)
    assert battery.soc <= 1.0  # SOC should not exceed 1.0

def test_esc_initialization():
    esc = ESC(I_max=10)
    assert esc.I_max == 10

def test_esc_limit_current_within_limit():
    esc = ESC(I_max=10)
    assert esc.limit(I=5) == 5

def test_esc_limit_current_above_limit():
    esc = ESC(I_max=10)
    assert esc.limit(I=15) == 10

def test_esc_limit_current_at_limit():
    esc = ESC(I_max=10)
    assert esc.limit(I=10) == 10

def test_esc_limit_current_negative():
    esc = ESC(I_max=10)
    assert esc.limit(I=-5) == -5  # Negative current should not be limited

def test_motor_initialization():
    motor = Motor(Kv=1000, R=0.1, I_max=20, P_max=500)
    assert motor.Kv == 1000
    assert motor.R == 0.1
    assert motor.I_max == 20
    assert motor.P_max == 500
    assert motor.Kt == 30 / (np.pi * 1000)

def test_motor_torque_current_normal_operation():
    motor = Motor(Kv=1000, R=0.1, I_max=20, P_max=500)
    Q, I, P = motor.torque_current(V_batt=12, omega=100)
    assert I <= 20
    assert P == 19.098593171027442
    assert Q == 0.19098593171027442

def test_motor_torque_current_zero_omega():
    motor = Motor(Kv=1000, R=0.1, I_max=20, P_max=500)
    Q, I, P = motor.torque_current(V_batt=12, omega=0)
    assert Q == 0.0
    assert P == 0.0

def test_motor_torque_current_power_limit():
    motor = Motor(Kv=1000, R=0.1, I_max=20, P_max=500)
    Q, I, P = motor.torque_current(V_batt=100, omega=100)
    assert I <= 20
    assert P == 19.098593171027442
    assert Q == 0.19098593171027442

def test_motor_torque_current_exceeds_power_limit():
    motor = Motor(Kv=1000, R=0.1, I_max=20, P_max=5)
    # Use a high V_batt and low omega to force high power
    Q, I, P = motor.torque_current(V_batt=100, omega=100)
    assert I <= 20
    assert P == 5  # Power should be limited to P_max
    assert Q == 5 / 100  # Torque should be adjusted to respect P_max


def test_motor_torque_current_negative_input():
    motor = Motor(Kv=1000, R=0.1, I_max=20, P_max=500)
    with pytest.raises(ValueError):
        motor.torque_current(V_batt=-1, omega=100)
    with pytest.raises(ValueError):
        motor.torque_current(V_batt=12, omega=-1)