#!/usr/bin/env python
from run_both import process_request
import numpy as np
import pylab as plt
import pickle
from io import BytesIO
from tqdm import tqdm

# from skopt import gp_minimize
from skopt import Optimizer
from skopt.plots import plot_convergence

# TARGET_COLOR = (20, 40, 110) # Dark blue
# TARGET_COLOR = (100, 20, 50) # Dark brown-reddish
# TARGET_COLOR = (20, 120, 40) # Dark green
# TARGET_COLOR = (35, 137, 94) # Dark green (reachable)
TARGET_COLOR = (132, 76, 87)  # Salmon (reachable)

WARMUP_TIME = 1
N_CALLS = 50

LOG = []
SHOW_FINAL_RESULT = True  # wether to test and show the final result


def color_cost_function_naive(measure_color, target_color):
    """Naive distance between colors (just Cartesian distance of RGB)"""
    return np.sum(np.abs(np.array(measure_color) - np.array(target_color)))


def color_cost_function_ciede(measure_color, target_color):
    """Advanced, perceptually uniform distance between colors"""
    # Note that rgb2lab expects the values to be from [0, 1], not [0, 255].
    # see https://stackoverflow.com/questions/67216690/knowing-which-distance-metric-to-use-for-color-differences-in-pixels-rgb
    from skimage.color import rgb2lab, deltaE_ciede2000

    distance = deltaE_ciede2000(
        rgb2lab(np.array(measure_color) / 255), rgb2lab(np.array(target_color) / 255)
    )

    return distance


color_cost_function = color_cost_function_ciede


def function_to_minimize(input_color):
    global TARGET_COLOR
    R, G, B = input_color
    rgb_color = (int(R), int(G), int(B))
    assert all(
        0 <= c <= 255 for c in rgb_color
    ), "RGB color values must be in the range [0, 255]"

    # HERE: call FINALES TO ASK TO MEASURE THE COLOR, INSTEAD, REPLACING THE FOLLOWING process_request
    # CHECK THAT THE RESULTS COME BACK INTO FINALES (BY POLLING)
    # WHEN THE RESULTS ARE READY, GET THEM FROM FINALES AND SET THEM IN measure_color
    measure_color = process_request(rgb_color, warmup_time=WARMUP_TIME)

    # print(f"LOG: IN={rgb_color}; OUT={measure_color}")
    LOG.append((rgb_color, measure_color))

    # Compute the cost function and return the cost to minimize (zero = the output color is the target one)
    return color_cost_function(measure_color, TARGET_COLOR)


if __name__ == "__main__":
    # See example https://scikit-optimize.github.io/stable/auto_examples/bayesian-optimization.html

    # Note: I already use the asynchronous variant (instead of directly calling `gp_minimize` with
    # a callback function) as it will be much easier to integrate with AiiDA or FINALES, where the
    # execution of the calculation can be very slow and it should be managed externally. See
    # https://scikit-optimize.github.io/stable/auto_examples/ask-and-tell.html

    opt = Optimizer(
        [(0, 255), (0, 255), (0, 255)],  # the bounds on each dimension of x
        base_estimator="GP",
        acq_func="gp_hedge",  # the acquisition function
        n_initial_points=5,
    )  # the number of random initialization points
    #                    noise="gaussian")

    for idx in tqdm(range(N_CALLS)):
        # Imagining this is a WorkChain, I already call with the prefix ctx_
        # what I would put in the context
        ctx_next_rgb = opt.ask()

        # I dump to file the state, as the next call in principle could then be a 'submit'
        # and the state needs to be retrieved
        pickled_io = BytesIO()
        pickle.dump(opt, pickled_io)
        pickled_io.seek(0)
        ctx_pickled = pickled_io.read()
        del pickled_io
        # In AiiDA, I would store this somewhere, e.g. (depending on its size)
        # e.g. in the context

        # Slow: this could be delegate/submitted
        ctx_rgb_eval = function_to_minimize(ctx_next_rgb)
        # I simulate what happens when opt goes out of scope at the end of a workchain step
        del opt

        # I imagine this is in the next "step" in the WorkChain outline: I need somehow
        # to retreive the state
        pickled_io = BytesIO()
        pickled_io.write(ctx_pickled)
        pickled_io.seek(0)
        opt = pickle.load(pickled_io)
        res = opt.tell(ctx_next_rgb, ctx_rgb_eval)

    print(
        f"Approximate minimum at {res.x} with cost function value {res.fun} (target: {TARGET_COLOR})"
    )
    # Here, I could pickle to file again if I want to plot in a different script
    plot_convergence(res)

    # if SHOW_FINAL_RESULT:
    #    plt.savefig('convergence_plot.png')
    #    print("Convergence plot saved to 'convergence_plot.png' in order to move on to test the final result")

    fig, axs = plt.subplots(len(LOG), 2, figsize=(8, 2 * len(LOG)))

    for idx, (in_rgb, out_rgb) in enumerate(LOG):
        axs[idx, 0].imshow(np.ones((100, 100, 3), dtype=np.uint8) * in_rgb)
        axs[idx, 0].axis("off")
        axs[idx, 1].imshow(np.ones((100, 100, 3), dtype=np.uint8) * out_rgb)
        axs[idx, 1].axis("off")

    axs[0, 0].set_title("Input color")
    axs[0, 1].set_title("Output (measured) color")
    plt.tight_layout()

    # if SHOW_FINAL_RESULT:
    #    plt.savefig('tested_colors.png')
    #    print("Tested colors saved to 'tested_colors.png' in order to move on to the final result")
    # else:
    #    plt.show()

    print()
    print(LOG)
    print()

    if SHOW_FINAL_RESULT:
        result = process_request(res.x)

        import matplotlib.pyplot as plt

        fig, axs = plt.subplots(1, 3, figsize=(10, 4))

        h = w = 100
        axs[0].imshow(np.ones((h, w, 3), dtype=np.uint8) * res.x)
        axs[0].set_title(
            f"Input color (best, optimized)\nRGB=({res.x[0]}, {res.x[1]}, {res.x[2]})\nExpected output distance: {res.fun:.2f}"
        )
        axs[0].axis("off")  # Hide the axis

        axs[1].imshow(np.ones((h, w, 3), dtype=np.uint8) * result)
        axs[1].set_title(
            f"Output (measured) color\n"
            f"(distance from target = {color_cost_function(result, TARGET_COLOR):.2f})\nRGB=({result[0]}, {result[1]}, {result[2]})"
        )
        axs[1].axis("off")  # Hide the axis

        axs[2].imshow(np.ones((h, w, 3), dtype=np.uint8) * TARGET_COLOR)
        axs[2].set_title(
            f"Desired (target) color\nRGB=({TARGET_COLOR[0]}, {TARGET_COLOR[1]}, {TARGET_COLOR[2]})"
        )
        axs[2].axis("off")  # Hide the axis

    else:
        print("You can test it with:")
        print(f"./run_both.py {res.x[0]} {res.x[1]} {res.x[2]}")

    plt.show()
