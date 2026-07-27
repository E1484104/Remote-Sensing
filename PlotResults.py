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
