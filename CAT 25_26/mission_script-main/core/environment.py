import numpy as np

from drone import Drone


class Env:
    def __init__(self, air_density=1.225):
        self.rho = air_density

    def ground_constraint(self, drone: Drone):
        if not drone.takeoff:
            drone.pos[1] = 0.0
            drone.v_body[1] = 0.0