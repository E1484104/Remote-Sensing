from ReadImage import BACKGROUND_IMAGE_COUNT, read_images
from ReadLVM import read_lvms
from ExportImages import prompt_and_copy_image_segments
from PlotResults import plot_image_comparison, plot_results

# ====== SPECIFY TARGET FOLDER PATH ======
TEST_INDEX = "Tester20_Move"
TEST_DATE = "20260729"
TARGET_IMAGE_1 = rf"..\{TEST_DATE}\{TEST_INDEX}\Cam1_Image"
TARGET_IMAGE_2 = rf"..\{TEST_DATE}\{TEST_INDEX}\Cam2_Image"
TARGET_LVM_1 = rf"..\{TEST_DATE}\{TEST_INDEX}\Cam1.lvm"
TARGET_LVM_2 = rf"..\{TEST_DATE}\{TEST_INDEX}\Cam2.lvm"
TARGET_EXTRACTED_IMAGE_1 = rf"..\{TEST_DATE}\{TEST_INDEX}\Cam1_Extracted_Image"
TARGET_EXTRACTED_IMAGE_2 = rf"..\{TEST_DATE}\{TEST_INDEX}\Cam2_Extracted_Image"
BG_NOISE = rf"..\{TEST_DATE}\{TEST_INDEX}\Cam2_Noise"

IMAGE_SIZE_1 = (40, 40)
IMAGE_SIZE_2 = (20, 20)
COPY_IMAGE_COUNT = 2000
SMOOTH_WINDOW = 20


def get_processing_settings(image_folder_name):

    if image_folder_name == TARGET_IMAGE_2:
        return {
            "image_size": IMAGE_SIZE_2,
            "remove_background": True,
        }

    if image_folder_name == TARGET_IMAGE_1:
        return {
            "image_size": IMAGE_SIZE_1,
            "remove_background": False,
        }

    raise ValueError(f"Unsupported camera name: {image_folder_name}")


if __name__ == '__main__':
    settings_cam1 = get_processing_settings(TARGET_IMAGE_1)
    settings_cam2 = get_processing_settings(TARGET_IMAGE_2)
    skip_count = BACKGROUND_IMAGE_COUNT
    image_results1 = read_images(
        TARGET_IMAGE_1,
        image_size=settings_cam1["image_size"],
        remove_background=settings_cam1["remove_background"],
        skip_count=skip_count,
    )
    image_results2 = read_images(
        TARGET_IMAGE_2,
        image_size=settings_cam2["image_size"],
        remove_background=settings_cam2["remove_background"],
        skip_count=skip_count,
        background_output_folder=BG_NOISE,
    )
    lvm_results1 = read_lvms(TARGET_LVM_1, skip_count=skip_count)
    lvm_results2 = read_lvms(TARGET_LVM_2, skip_count=skip_count)
    # plot_results(image_results1, lvm_results1)  # Remote
    # plot_results(image_results2, lvm_results2)  # Contact
    plot_image_comparison(image_results1, image_results2, smooth_window=SMOOTH_WINDOW)

    copied_result = prompt_and_copy_image_segments(
        {
            "cam1": {
                "source_folder": TARGET_IMAGE_1,
                "output_root": TARGET_EXTRACTED_IMAGE_1,
            },
            "cam2": {
                "source_folder": TARGET_IMAGE_2,
                "output_root": TARGET_EXTRACTED_IMAGE_2,
            },
        },
        skip_count=skip_count,
        image_count=COPY_IMAGE_COUNT,
    )

    if copied_result is not None:
        start_index = copied_result["start_index"]
        copied_count = min(
            len(copied_segment["selected_paths"])
            for copied_segment in copied_result["copied_segments"].values()
        )
        end_index = start_index + copied_count

        plot_image_comparison(
            image_results1[start_index:end_index],
            image_results2[start_index:end_index],
            start_index=start_index,
            smooth_window=SMOOTH_WINDOW,
        )
