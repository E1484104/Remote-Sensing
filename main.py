from ReadImage import read_images
from ReadLVM import read_lvms
from PlotResults import plot_results

# ====== SPECIFY TARGET FOLDER PATH ======
TARGET_FOLDER = r"..\20260724\data\test1_image\cam2"
TARGET_LVM = r"..\20260724\data\Cam2_test1.lvm"


if __name__ == '__main__':
    image_results = read_images(TARGET_FOLDER)
    lvm_results = read_lvms(TARGET_LVM)
    plot_results(image_results, lvm_results)
