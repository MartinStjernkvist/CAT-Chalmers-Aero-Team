import numpy as np
import time
import os
from scrape import get_cl_cd
import copy

# TODO implement a great PID that removes occilations

class Drone:
    def __init__(
        self,
        mass=5.0,
        v_thresh=1e-6,
        wing_area=0.8,
        thrust=150.0,
        battery_capacity_wh=500.0,
        path="../prop/aero",
    ):
        self.mass = mass
        self.v_thresh = v_thresh
        self.wing_area = wing_area
        self.thrust_max = thrust
        self.wh_used = 0
        self.battery_capacity_wh = battery_capacity_wh
        self.path = path
        self.angle = None

    def reset(self):
        # TODO necessary?
        self.pos = np.array([0.0, 0.0])
        self.v_body = np.array([0.0, 0.0])
        self.t = 0.0
        self.wh_used = 0
        self.battery_wh = getattr(self, "battery_capacity_wh", 0.0)
        self.li_vec = np.array([0.0, 0.0])
        self.dr_vec = np.array([0.0, 0.0])
        self.th_vec = np.array([0.0, 0.0])
        self.f_vec = np.array([0.0, 0.0])
        self.angle = None

        self.takeoff = False
        self.climbed = False
        self.cruised = False

        return self

    def update_values(self, rho):
        # TODO generate a dataframe with all these values in the beginning
        # have call functions to get the nearest cl, cd - steal from get_cl_cd
        x, y = self.v_norm
        angle = np.arctan2(y, x)
        v_abs = np.linalg.norm(self.v_body)
        cl, cd, _, _ = get_cl_cd(v_abs, angle, self.path)
        self.rho = rho
        self.cl = cl
        self.cd = cd

    def weight_vec(self):
        return np.array([0.0, -self.mass * 9.81])

    @property
    def v_norm(self):
        v_abs = np.linalg.norm(self.v_body)
        if self.v_low:
            # low speed => v norm is [1,0]
            return np.array([1.0, 0])
        else:
            return self.v_body / v_abs

    @property
    def v_low(self):
        return np.linalg.norm(self.v_body) < self.v_thresh

    def lift_vec(self):
        v_abs = np.linalg.norm(self.v_body)
        if self.v_low:
            # low speed => up is [0,1]
            lift_dir = np.array([0.0, 1.0])
        else:
            vx, vy = self.v_norm
            # rotate 90
            lift_dir = np.array([-vy, vx])
        lift_abs = 0.5 * self.rho * v_abs**2 * self.wing_area * self.cl
        return lift_abs * lift_dir

    def drag_vec(self):
        v_abs = np.linalg.norm(self.v_body)
        if self.v_low:
            return np.zeros(2)
        drag_abs = 0.5 * self.rho * v_abs**2 * self.wing_area * self.cd
        return -drag_abs * self.v_norm

    def thrust_vec(self):
        x, y = self.v_norm
        self.start = False
        angle = np.rad2deg(np.atan2(y,x))
        if  angle >= self.angle and self.takeoff:
            self.start = True
        thrust_vec = self.thrust_max * self.v_norm
        if self.start:
            x_angle = np.cos(np.deg2rad(angle))
            y_angle = np.sin(np.deg2rad(angle))
            thrust_vec = 0.35 * thrust_vec * np.array([x_angle,y_angle])
        return thrust_vec

    def calculate_thrust(self):
        # TODO use a PID instead
        dr = copy.deepcopy(self)
        w_vec = self.weight_vec()
        th_vec = self.thrust_max
        v_body = self.v_body

        interpolants = 100
        for v_ratio in np.linspace(0, 1, interpolants):
            dr.v_body = v_body * v_ratio
            for thrust_ratio in np.linspace(0, 1, interpolants):
                li_vec = dr.lift_vec()
                dr_vec = dr.drag_vec()
                f_vec = li_vec + dr_vec + th_vec * thrust_ratio + w_vec
                x, y = f_vec
                f_vec_angle = np.rad2deg(np.atan((y/x)))
                print(self.angle, f_vec_angle, "\t" ) # TODO here ALSKDJFASLDJKFÖALKSDJFÖLASJDFÖLKJASÖDLJFAÖLSKDJFÖLAJSDFÖLKJ
                time.sleep(0.01)
                # print(np.rad2deg(np.atan2(y, x)))
                # time.sleep(0.001)
                # print(self.angle, np.rad2deg(np.atan2(y,x)))
                if self.angle >= np.rad2deg(np.atan2(y, x)):
                    pass
                #    return drone.th_vec
        raise RuntimeError(f"Could not find thrust for angle {self.angle}")

    def power_required(self):
        if self.v_low:
            return 0.0
        drag_vec = self.drag_vec()
        power_shaft = abs(np.dot(drag_vec, self.v_body))
        return power_shaft

    def consume_energy(self, power_w, dt):
        self.wh_used = (power_w * dt) / 3600.0
        self.battery_wh = max(0.0, self.battery_wh - self.wh_used)
        return self.wh_used

    def compute_forces(self, rho):
        self.update_values(rho)
        self.li_vec = self.lift_vec()
        self.dr_vec = self.drag_vec()
        self.th_vec = self.thrust_vec()
        self.weight = self.weight_vec()
        self.f_vec = self.li_vec + self.dr_vec + self.th_vec + self.weight
        return self.f_vec

    def step(self, env, force_vec, dt):
        self.v_body += force_vec / self.mass * dt
        env.ground_constraint(self)  # place angle constraint here
        self.pos += self.v_body * dt
        self.t += dt
        power = self.power_required()
        self.consume_energy(power, dt)
