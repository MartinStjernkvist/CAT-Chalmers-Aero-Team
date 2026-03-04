import numpy as np
from drone import Drone
from environment import Env
from simulator import Sim, Takeoff, Climb, Cruise
from analyzer import Analyzer, Point

def main():
    drone = Drone(
        mass=5.0,
        wing_area=0.9,
        thrust=50.0,
        path="prop/aero",
    )

    env = Env(air_density=1.225)
    sim = Sim(drone=drone, env=env, dt=0.01)

    vis_points = [
        # Point(key=("t", "battery_wh")),
        # Point(dara = "weigth"),
        Point(
            key="pos",
            data=("f_vec", "li_vec", "dr_vec", "th_vec", "weight"),
            interpolants=200,
            normalized=False,
        ),
    ]

    print_args = [
        "li_vec",
        "dr_vec",
        "th_vec",
        "weight",
        "f_vec",
        "v_body",
        "pos",
    ]

    vis_an_to = Analyzer(vis_points=vis_points)
    print_an_to = Analyzer(print_args=print_args)

    sim.run(Takeoff(angle=0, runway_length=20, analyzer=vis_an_to))
    sim.run(Climb(angle=7, altitude_goal=100, analyzer=vis_an_to))
    #sim.run(Cruise(angle=0, distance_goal=500, analyzer=vis_an_to))

    vis_an_to.show_data(
        size=(5, 3), color=("Black", "Red", "Blue", "Green", "Purple", "Yellow")
    )
    # vis_an_cl.show_data(size=(5, 3), color="Black")


if __name__ == "__main__":
    main()

# TODO get some good scraping from the motors and thrust,
# use that to get good takeoff metrics

# TODO measure time and iterations, give some sort of
# presentation of this in the show

# TODO other way around of collecting data, recording everything
# and scraping after, good for jupyter

# MARTIN HAR TALAT
# TODO sätt värden för takeoff, cruise och climb innan vi kör scriptet
# TODO gör superförenklingar för transition-periods, legit bara rotationer
# TODO cruise och climb konstant hastighet
