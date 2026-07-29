from pathlib import Path
import re

import cv2
import numpy as np

# ====== SPECIFY IMAGE SUFFIX ======
IMAGE_SUFFIXES = {".png"}
BACKGROUND_IMAGE_COUNT = 3000

# ====== ENSURE IMAGE NAME ENDS WITH ITS INDEX ======
def image_number_sort_key(image_path):
    match = re.search(r"(\d+)$", image_path.stem)
    if match is None:
        raise ValueError(f"Image filename does not end with a number: {image_path}")
    return int(match.group(1))

# ====== ENSURE IMAGE DATA TYPE IS U16 ======
def image_to_u16_matrix(image, image_path, image_size):
    if image.ndim != 2:
        raise ValueError(
            f"Expected a 2D image, got shape {image.shape}: {image_path}"
        )

    expected_height, expected_width = image_size
    if image.shape != (expected_height, expected_width):
        raise ValueError(
            f"Expected image size {expected_width}x{expected_height}, "
            f"got {image.shape[1]}x{image.shape[0]}: {image_path}"
        )

    if image.dtype == np.uint16:
        return image.copy()
    if image.dtype == np.uint8:
        return image.astype(np.uint16)

    if np.issubdtype(image.dtype, np.integer):
        return np.clip(image, 0, 65535).astype(np.uint16)

    raise TypeError(f"Unsupported image dtype {image.dtype}: {image_path}")


def process_image(image_matrix, image_path):
    # print(f"Calculating: {image_path}")
    # print(f"Matrix shape: {image_matrix.shape}, dtype: {image_matrix.dtype}")

    mean_value = np.mean(image_matrix)
    std_value = np.std(image_matrix)
    # print(f"Mean: {mean_value}, Std: {std_value}")

    if std_value == 0:
        raise ZeroDivisionError(f"Standard deviation is zero: {image_path}")

    result = (mean_value / std_value) ** 2
    # print(f"Result: {result}")
    # print("")
    return result


def read_image_matrix(image_path, image_size):
    image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    return image_to_u16_matrix(image, image_path, image_size)


def get_sorted_image_paths(folder_path):
    target_folder = Path(folder_path)

    if not target_folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {target_folder}")
    if not target_folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {target_folder}")

    image_paths = []
    for item in target_folder.iterdir():
        if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES:
            image_paths.append(item)

    return sorted(image_paths, key=image_number_sort_key)


def get_result_image_paths(folder_path, skip_count=0):
    if skip_count < 0:
        raise ValueError(f"skip_count must not be negative, got {skip_count}")

    sorted_image_paths = get_sorted_image_paths(folder_path)

    if skip_count > len(sorted_image_paths):
        raise ValueError(
            f"skip_count is larger than image count, skip_count={skip_count}, "
            f"image count={len(sorted_image_paths)}"
        )

    return sorted_image_paths[skip_count:]


def calculate_background_noise(image_paths, image_size):
    if len(image_paths) < BACKGROUND_IMAGE_COUNT:
        raise ValueError(
            f"Need at least {BACKGROUND_IMAGE_COUNT} images to calculate background noise, "
            f"got {len(image_paths)}"
        )

    background_sum = np.zeros(image_size, dtype=np.float64)

    for image_path in image_paths[:BACKGROUND_IMAGE_COUNT]:
        image_matrix = read_image_matrix(image_path, image_size)
        background_sum += image_matrix

    background_noise = background_sum / BACKGROUND_IMAGE_COUNT

    if np.any(background_noise == 0):
        raise ZeroDivisionError("Background noise contains zero value")

    return background_noise


def read_images(folder_path, image_size, remove_background=False, skip_count=0):
    if skip_count < 0:
        raise ValueError(f"skip_count must not be negative, got {skip_count}")
    if len(image_size) != 2:
        raise ValueError(f"image_size must be (height, width), got {image_size}")

    sorted_image_paths = get_sorted_image_paths(folder_path)

    if skip_count > len(sorted_image_paths):
        raise ValueError(
            f"skip_count is larger than image count, skip_count={skip_count}, "
            f"image count={len(sorted_image_paths)}"
        )

    background_noise = None
    if remove_background:
        background_noise = calculate_background_noise(sorted_image_paths, image_size)

    result_image_paths = sorted_image_paths[skip_count:]

    actual_results = []
    for image_path in result_image_paths:
        image_matrix = read_image_matrix(image_path, image_size)

        if remove_background:
            image_matrix = image_matrix / background_noise

        result = process_image(image_matrix, image_path)
        actual_results.append(result)

    return actual_results
