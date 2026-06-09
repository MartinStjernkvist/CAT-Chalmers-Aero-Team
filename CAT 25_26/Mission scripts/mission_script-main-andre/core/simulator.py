import numpy as np
import time

from analyzer import Analyzer
from drone import Drone
from environment import Env


class Sim:
    def __init__(self, drone: Drone, env: Env, dt=0.1):
        self.drone = drone.reset()
        self.env = env
        self.dt = dt

    def run(self, mission):
        mission.run(self)


class Mission:
    def __init__(self, angle, analyzer: Analyzer | None = None):
        self.analyzer = analyzer
        self.angle = angle

    def on_start(self, sim: Sim):
        x = np.cos(np.deg2rad(self.angle))
        y = np.sin(np.deg2rad(self.angle))
        sim.drone.angle = self.angle
        sim.drone.v_body = np.linalg.norm(sim.drone.v_body) * np.array([x, y])
        sim.drone.th_vec = np.linalg.norm(sim.drone.f_vec) * np.array([x, y])
        sim.drone.compute_forces(sim.env.rho)

    def on_step(self, sim: Sim):
        pass

    def on_end(self, sim: Sim):
        pass

    def simulate_condition(self, sim: Sim):
        raise NotImplementedError

    def success_check(self, sim: Sim):
        raise NotImplementedError

    def log(self, drone: Drone):
        if self.analyzer != None:
            self.analyzer.get_data(drone)

    def run(self, sim: Sim):
        self.on_start(sim)
        drone = sim.drone
        self.log(drone)
        while self.simulate_condition(sim):
            force_vec = drone.compute_forces(sim.env.rho)
            drone.step(sim.env, force_vec, sim.dt)
            self.on_step(sim)
            self.log(drone)
            if self.success_check(sim):
                break
        self.on_end(sim)
        return self


class Takeoff(Mission):
    def __init__(self, runway_length, angle, analyzer: Analyzer | None = None):
        super().__init__(angle=angle, analyzer=analyzer)
        self.runway_length = runway_length

    def simulate_condition(self, sim: Sim):
        drone = sim.drone
        return (not drone.takeoff) and (drone.pos[0] < self.runway_length)

    def success_check(self, sim: Sim):
        if sim.drone.compute_forces(sim.env.rho)[1] >= 0:
            sim.drone.takeoff = True
            return True
        return False

    def on_end(self, sim: Sim):
        sim.drone.takeoff = True


class Climb(Mission):
    def __init__(self, altitude_goal, angle, analyzer: Analyzer | None = None):
        super().__init__(angle=angle, analyzer=analyzer)
        self.altitude_goal = altitude_goal

    def simulate_condition(self, sim: Sim):
        drone = sim.drone
        return (not drone.climbed) and (drone.pos[1] < self.altitude_goal)

    def success_check(self, sim: Sim):
        if sim.drone.pos[1] >= self.altitude_goal:
            sim.drone.climbed = True
            return True
        return False


class Cruise(Mission):
    def __init__(self, distance_goal, angle, analyzer: Analyzer | None = None):
        super().__init__(angle=angle, analyzer=analyzer)
        self.distance_goal = distance_goal
        self.distance_traveled = 0

    def simulate_condition(self, sim: Sim):
        drone = sim.drone
        return (not drone.cruised) and (self.distance_traveled < self.distance_goal)

    def success_check(self, sim: Sim):
        if self.distance_traveled < self.distance_goal:
            sim.drone.cruised = True
            return True
        return False
