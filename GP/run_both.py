#!/usr/bin/env python
from show_color import show_fullscreen_color, stop_pygame
from get_image import get_average_color_full


## TODO: REPLACE THIS WITH THE CALL TO FINALES: 
## - MONITOR IF FINALES HAS RGB_COLORS TO PROCESS
## - CALL THE FUNCTION
## - WHEN IT IS DONE, SEND THE RESULTS BACK TO FINALES
def process_request(rgb_color, warmup_time=1, show_image=False):
    try:
        # show the color, do not close the window
        show_fullscreen_color(rgb_color, None)

        # get the average color from the webcam
        average_color = get_average_color_full(device_number=0, show_image=show_image, verbose=False, warmup_time=warmup_time)
        return average_color
    
    finally:
        # Make sure to close the full-screen window
        stop_pygame()

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        rgb_color = (int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    else:
        print("USING DEFAULT COLOR!")
        rgb_color = (155, 222, 180) 
    captured_rgb = process_request(rgb_color, show_image=True)
    print(f"Input: {rgb_color}, Captured: {captured_rgb}")

