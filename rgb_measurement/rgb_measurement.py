#!/usr/bin/env python

from show_color import show_fullscreen_color, stop_pygame
from get_image import get_average_color_full


def measure_rgb_from_snapshot(id, R, G, B, warmup_time=1):
    try:
        show_fullscreen_color((R, G, B), None)

        avg_R, avg_G, avg_B = get_average_color_full(
            device_number=0,
            show_image=False,
            verbose=False,
            warmup_time=warmup_time,
        )

        # Take snapshot and return computed average color
        return {
            "id": id,
            "R": avg_R,
            "G": avg_G,
            "B": avg_B,
        }

    finally:
        stop_pygame()


def simulate_rgb_measurement(id, R, G, B, warmup_time=1):
    return {
        "id": id,
        "R": min(R + 10, 255),
        "G": min(G + 10, 255),
        "B": min(B + 10, 255),
    }
