import matplotlib.pyplot as plt


def plot_results(image_results, lvm_results):

    if len(image_results) != len(lvm_results):
        print("Image results length:", len(image_results))
        print("LVM results length:", len(lvm_results))
        print("Length of data do not match")
        return

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
    plt.title("Image Results vs LVM Results")
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


def plot_image_comparison(cam1_results, cam2_results):

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

    indices = range(len(cam1_results))

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
    ax1.set_title("Cam1 vs Cam2 Image Results")
    ax1.grid(True, alpha=0.3)

    lines = line1 + line2
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="upper right")

    plt.tight_layout()
    plt.show()
