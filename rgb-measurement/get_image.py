#!/usr/bin/env python
import cv2
import time
import numpy as np


def list_available_webcams(max_index=10):
    available_webcams = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
            contrast = cap.get(cv2.CAP_PROP_CONTRAST)
            res = {
                "index": index,
                "frame_width": frame_width,
                "frame_height": frame_height,
                "fps": fps,
                "brightness": brightness,
                "contrast": contrast,
            }
            cap.release()
            available_webcams.append(res)

            # Get the name on linux with:
            # sudo apt-get install v4l-utils
            # v4l2-ctl --device=/dev/video{index} --info
        else:
            # If an index returns an error, I stop (not sure if I might miss some webcams)
            # This issues a warning. Could be suppresseed if needed.
            # On Linux one could also just check /dev/video{index} if it exists
            # (even if on my machine I have video0 to video3, but I only see one here)
            break
    return available_webcams


def initialize_webcam(
    device_number=0, brightness=0.9, contrast=0.5, warmup_time=0, verbose=False
):
    if verbose:
        print("Initializing webcam...")
    # Initialize the webcam
    cap = cv2.VideoCapture(device_number)

    if verbose:
        print("Setting brightness and contrast...")
    # Set brightness and contrast
    cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
    cap.set(cv2.CAP_PROP_CONTRAST, contrast)

    # if verbose:
    #    print("Waiting warm-up time...")
    # Warm up the webcam for some seconds
    # NOTE: does not seem to be necessary on Linux with the Logitech camera,
    # I think the driver does it internally when initializing the class.
    # It is instead needed on Mac, otherwise you get a black image.
    time.sleep(warmup_time)
    return cap


def get_average_color(cap, show_image=False, verbose=False):
    if verbose:
        print("Getting image...")
    # Capture a frame
    ret, frame = cap.read()

    if ret:
        if verbose:
            print("Captured image successfully, displaying the captured image...")
        # Save the captured frame to a file
        # cv2.imwrite('captured_image.jpg', frame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # print(frame_rgb.shape) # (480, 640, 3) -> (h, w, color channel = RGB)
        h, w = frame_rgb.shape[:2]

        central_frame_rgb = frame_rgb[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4, :]

        average_color = central_frame_rgb.mean(axis=(0, 1)).astype(np.uint8)

        if verbose:
            print(f"Average color: {average_color}")

        # Display the frame using matplotlib
        if show_image:
            import matplotlib.pyplot as plt

            ## Set the matplotlib backend to TkAgg
            # import matplotlib
            # matplotlib.use('TkAgg')

            fig, axs = plt.subplots(1, 2)

            axs[0].imshow(central_frame_rgb)
            axs[0].set_title("Central part of captured image")
            axs[0].axis("off")  # Hide the axis

            average_color_image = np.ones((h, w, 3), dtype=np.uint8) * average_color
            axs[1].imshow(average_color_image)
            axs[1].set_title("Average color")
            axs[1].axis("off")  # Hide the axis

            plt.show()
        return average_color
    else:
        raise RuntimeError("Failed to capture image")


def close_webcam(cap, verbose=False):
    if verbose:
        print("Release webcam and close windows...")
    # Release the webcam and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


def get_average_color_full(
    device_number=0, warmup_time=0, show_image=False, verbose=False
):
    cap = initialize_webcam(
        device_number=device_number, warmup_time=warmup_time, verbose=verbose
    )
    average_color = get_average_color(cap, show_image=show_image, verbose=verbose)
    close_webcam(cap, verbose=verbose)
    return average_color


if __name__ == "__main__":
    DO_LIST_WEBCAMS = (
        False  # Set to True to list all available webcams; requires a few seconds
    )

    if DO_LIST_WEBCAMS:
        # List all available webcam indices
        webcams = list_available_webcams()
        print("Available webcams:", webcams)

    average_color = get_average_color_full(
        device_number=0, show_image=True, verbose=False, warmup_time=2
    )
    print("Average color:", average_color)
