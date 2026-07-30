import matplotlib.pyplot as plt
import numpy as np


def smooth_results(results, window_size):
    if window_size is None:
        return list(results)
    if window_size <= 0:
        raise ValueError(f"window_size must be positive, got {window_size}")

    values = np.asarray(results, dtype=float)
    if values.size == 0 or window_size == 1:
        return values.tolist()

    effective_window = min(window_size, values.size)
    left_padding = (effective_window - 1) // 2
    right_padding = effective_window // 2
    padded_values = np.pad(values, (left_padding, right_padding), mode="edge")
    kernel = np.ones(effective_window, dtype=float) / effective_window

    return np.convolve(padded_values, kernel, mode="valid").tolist()


def plot_results(image_results, lvm_results, smooth_window=None):

    if len(image_results) != len(lvm_results):
        print("Image results length:", len(image_results))
        print("LVM results length:", len(lvm_results))
        print("Length of data do not match")
        return

    image_results = smooth_results(image_results, smooth_window)
    lvm_results = smooth_results(lvm_results, smooth_window)

    n = len(image_results)
    print("Results length:", n)

    difference = []
    for index in range(n):
        difference.append(image_results[index] - lvm_results[index])

    plt.figure(figsize=(14, 8), dpi=150)

    # Raw data in one image
    plt.subplot(2, 1, 1)
    plt.plot(image_results, label="Image Results", color="tab:blue", linewidth=0.8, alpha=0.8, zorder=2)
    plt.plot(lvm_results, label="LVM Results", color="tab:orange", linewidth=0.8, alpha=0.6, zorder=1)

    plt.ylabel("Result")
    if smooth_window is None:
        plt.title("Image Results vs LVM Results")
    else:
        plt.title(f"Image Results vs LVM Results (smoothed, window={smooth_window})")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Data difference
    plt.subplot(2, 1, 2)
    plt.plot(difference, label="Image - LVM", color="tab:red", linewidth=0.7)
    plt.axhline(0, color="black", linewidth=0.8, alpha=0.6)
    plt.xlabel("Index")
    plt.ylabel("Difference")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def plot_image_comparison(cam1_results, cam2_results, start_index=0, smooth_window=None):

    if len(cam1_results) != len(cam2_results):
        print("Cam1 results length:", len(cam1_results))
        print("Cam2 results length:", len(cam2_results))
        print("Data do not match")
        return

    if len(cam1_results) == 0:
        print("Cam1 results length:", len(cam1_results))
        print("Cam2 results length:", len(cam2_results))
        print("No data available for comparison")
        return

    indices = range(start_index, start_index + len(cam1_results))
    cam1_results = smooth_results(cam1_results, smooth_window)
    cam2_results = smooth_results(cam2_results, smooth_window)

    print("Cam1 results length:", len(cam1_results))
    print("Cam2 results length:", len(cam2_results))

    fig, ax1 = plt.subplots(figsize=(14, 6), dpi=150)
    ax2 = ax1.twinx()

    line1 = ax1.plot(
        indices,
        cam1_results,
        label="Cam1 Image Results",
        color="tab:blue",
        linewidth=0.8,
        alpha=0.85,
    )
    line2 = ax2.plot(
        indices,
        cam2_results,
        label="Cam2 Image Results",
        color="tab:orange",
        linewidth=0.8,
        alpha=0.75,
    )

    ax1.set_xlabel("Index")
    ax1.set_ylabel("Cam1 Result", color="tab:blue")
    ax2.set_ylabel("Cam2 Result", color="tab:orange")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:orange")
    if start_index == 0:
        title = "Cam1 vs Cam2 Image Results"
    else:
        end_index = start_index + len(cam1_results) - 1
        title = f"Cam1 vs Cam2 Image Results ({start_index}-{end_index})"
    if smooth_window is not None:
        title = f"{title} (smoothed, window={smooth_window})"
    ax1.set_title(title)
    ax1.grid(True, alpha=0.3)

    lines = line1 + line2
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="upper right")

    plt.tight_layout()
    plt.show()
