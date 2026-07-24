from pathlib import Path
import re

import cv2
import numpy as np

# ====== SPECIFY IMAGE SUFFIX AND IMAGE SIZE ======
IMAGE_SUFFIXES = {".png"}
IMAGE_SIZE = (40, 40)

# ====== ENSURE IMAGE NAME ENDS WITH ITS INDEX ======
def image_number_sort_key(image_path):
    match = re.search(r"(\d+)$", image_path.stem)
    if match is None:
        raise ValueError(f"Image filename does not end with a number: {image_path}")
    return int(match.group(1))

# ====== ENSURE IMAGE DATA TYPE IS U16 ======
def image_to_u16_matrix(image, image_path):
    if image.ndim != 2:
        raise ValueError(
            f"Expected a 2D image, got shape {image.shape}: {image_path}"
        )

    expected_height, expected_width = IMAGE_SIZE
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
    print(f"Calculating: {image_path}")
    print(f"Matrix shape: {image_matrix.shape}, dtype: {image_matrix.dtype}")

    mean_value = np.mean(image_matrix)
    std_value = np.std(image_matrix)
    print(f"Mean: {mean_value}, Std: {std_value}")

    if std_value == 0:
        raise ZeroDivisionError(f"Standard deviation is zero: {image_path}")

    result = (mean_value / std_value) ** 2
    print(f"Result: {result}")
    print("")
    return result


def read_images(folder_path):
    target_folder = Path(folder_path)

    if not target_folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {target_folder}")
    if not target_folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {target_folder}")

    image_paths = []
    for image_path in target_folder.iterdir():
        if image_path.is_file() and image_path.suffix.lower() in IMAGE_SUFFIXES:
            image_paths.append(image_path)

    actual_results = []
    for image_path in sorted(image_paths, key=image_number_sort_key):
        image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            print(f"Skip unreadable image: {image_path}")
            continue

        image_matrix = image_to_u16_matrix(image, image_path)
        result = process_image(image_matrix, image_path)
        actual_results.append(result)

    return actual_results
