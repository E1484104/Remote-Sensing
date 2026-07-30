import argparse
import re
from pathlib import Path

import cv2
import numpy as np

from ReadImage import IMAGE_SUFFIXES, image_to_u16_matrix


DEFAULT_OUTPUT_SUFFIX = "_csv_arrays"


def natural_sort_key(path):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


def get_image_paths(folder_path, image_suffixes=IMAGE_SUFFIXES, recursive=True):
    target_folder = Path(folder_path)

    if not target_folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {target_folder}")
    if not target_folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {target_folder}")

    items = target_folder.rglob("*") if recursive else target_folder.iterdir()
    image_paths = [
        item for item in items if item.is_file() and item.suffix.lower() in image_suffixes
    ]

    if not image_paths:
        raise FileNotFoundError(
            f"No supported images found in {target_folder}; "
            f"supported suffixes: {sorted(image_suffixes)}"
        )

    return sorted(image_paths, key=natural_sort_key)


def read_2d_image_array(image_path, dtype="uint16"):
    image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    if image.ndim != 2:
        raise ValueError(
            f"Expected a 2D grayscale image, got shape {image.shape}: {image_path}"
        )

    if dtype == "preserve":
        return image.copy()
    if dtype == "uint16":
        return image_to_u16_matrix(image, image_path, image.shape)

    raise ValueError(f"Unsupported dtype mode: {dtype}")


def get_default_output_folder(folder_path):
    input_folder = Path(folder_path)
    return input_folder.with_name(f"{input_folder.name}{DEFAULT_OUTPUT_SUFFIX}")


def export_image_arrays(
    folder_path,
    output_folder=None,
    dtype="uint16",
    overwrite=False,
    output_format="csv",
    recursive=True,
    progress_interval=100,
):
    if progress_interval <= 0:
        raise ValueError(f"progress_interval must be positive, got {progress_interval}")

    source_folder = Path(folder_path)
    image_paths = get_image_paths(source_folder, recursive=recursive)
    output_folder = (
        Path(output_folder)
        if output_folder is not None
        else get_default_output_folder(source_folder)
    )
    output_folder.mkdir(parents=True, exist_ok=True)

    total_count = len(image_paths)
    print(f"Found {total_count} PNG images.", flush=True)
    print(f"Source folder: {source_folder}", flush=True)
    print(f"Output folder: {output_folder}", flush=True)

    converted_count = 0
    current_folder = None

    for image_index, image_path in enumerate(image_paths, start=1):
        relative_image_path = image_path.relative_to(source_folder)
        relative_folder = relative_image_path.parent
        array_path = output_folder / relative_image_path.with_suffix(f".{output_format}")

        if relative_folder != current_folder:
            folder_display = "." if str(relative_folder) == "." else str(relative_folder)
            print(
                f"[{image_index}/{total_count}] Processing folder: {folder_display}",
                flush=True,
            )
            current_folder = relative_folder

        if image_index == 1 or image_index % progress_interval == 0:
            print(
                f"  Converting image {image_index}/{total_count}: {relative_image_path}",
                flush=True,
            )

        if array_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output array already exists: {array_path}. "
                "Use overwrite=True or --overwrite to replace existing files."
            )

        image_array = read_2d_image_array(image_path, dtype=dtype)
        array_path.parent.mkdir(parents=True, exist_ok=True)

        if output_format == "csv":
            save_array_as_csv(image_array, array_path)
        elif output_format == "npy":
            np.save(array_path, image_array)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        converted_count += 1
        if image_index % progress_interval == 0 or image_index == total_count:
            print(f"  Saved {converted_count}/{total_count} files.", flush=True)

    return output_folder, converted_count


def save_array_as_csv(image_array, csv_path):
    fmt = "%d" if np.issubdtype(image_array.dtype, np.integer) else "%.10g"
    np.savetxt(csv_path, image_array, delimiter=",", fmt=fmt)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Recursively convert all PNG images in a folder and its subfolders "
            "to visible 2D array files."
        )
    )
    parser.add_argument(
        "folder_path",
        help="Root folder containing PNG images, including images in subfolders.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_folder",
        help="Output folder for array files. Defaults to '<input_folder>_csv_arrays'.",
    )
    parser.add_argument(
        "--dtype",
        choices=("uint16", "preserve"),
        default="uint16",
        help="Use uint16 for existing project processing, or preserve original image dtype.",
    )
    parser.add_argument(
        "--format",
        choices=("csv", "npy"),
        default="csv",
        help="Output format. CSV is readable in Excel and text editors.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing output files in the output folder.",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_false",
        dest="recursive",
        help="Only convert images directly inside the input folder.",
    )
    parser.add_argument(
        "--progress-interval",
        type=int,
        default=100,
        help="Print image progress every N files.",
    )
    return parser


def main():
    args = build_arg_parser().parse_args()
    output_folder, converted_count = export_image_arrays(
        args.folder_path,
        output_folder=args.output_folder,
        dtype=args.dtype,
        overwrite=args.overwrite,
        output_format=args.format,
        recursive=args.recursive,
        progress_interval=args.progress_interval,
    )
    print(f"Converted {converted_count} images to 2D {args.format.upper()} arrays.")
    print(f"Output folder: {output_folder}")


if __name__ == "__main__":
    main()
