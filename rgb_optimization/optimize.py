#!/usr/bin/env python
from time import time

import numpy as np
import requests
from skopt import Optimizer

METHOD = "RGB-simulation"

WARMUP_TIME = 1
N_CALLS = 50

FINALES = "http://localhost:13371"
USER = "c2649110-614f-46f8-b7d1-a40fd9d0d95c"


def color_cost_function_naive(measured_color, target_color):
    """Naive distance between colors (just Cartesian distance of RGB)"""
    return np.sum(np.abs(np.array(measured_color) - np.array(target_color)))


def color_cost_function_ciede(measured_color, target_color):
    """Advanced, perceptually uniform distance between colors"""
    # Note that rgb2lab expects the values to be from [0, 1], not [0, 255].
    # see https://stackoverflow.com/questions/67216690/knowing-which-distance-metric-to-use-for-color-differences-in-pixels-rgb
    from skimage.color import deltaE_ciede2000, rgb2lab

    return deltaE_ciede2000(
        rgb2lab(np.array(measured_color) / 255),
        rgb2lab(np.array(target_color) / 255),
    )


color_cost_function = color_cost_function_ciede


def function_to_minimize(input_color, target_color):
    R, G, B = [int(c) for c in input_color]

    assert all(
        0 <= c <= 255 for c in [R, G, B]
    ), "RGB color values must be in the range [0, 255]"

    request_id = requests.post(
        f"{FINALES}/POST/request",
        json={
            "quantity": "rgb-measurement",
            "methods": [METHOD],
            "parameters": {
                METHOD: {
                    "R": R,
                    "G": G,
                    "B": B,
                    "warmup_time": WARMUP_TIME,
                }
            },
        },
    )

    while True:
        response = requests.get(f"{FINALES}/requests/{request_id}")

        if response.json()["status"] == "resolved":
            response = requests.get(f"{FINALES}/results/{request_id}")
            break

        time.sleep(15)

    measured_rgb = response.json()["data"]["rgb-measurement"]

    return color_cost_function(measured_rgb, target_color)


def optimize_rgb(id, R, G, B, n_calls):
    opt = Optimizer(
        [(0, 255), (0, 255), (0, 255)],
        base_estimator="GP",
        acq_func="gp_hedge",
        n_initial_points=5,
    )

    for _ in range(n_calls):
        next_rgb = opt.ask()
        rgb_eval = function_to_minimize(next_rgb, (R, G, B))
        res = opt.tell(next_rgb, rgb_eval)
        # TODO log the results

    return {
        "id": id,
        "minimum": res.x,
        "cost": res.fun,
    }
