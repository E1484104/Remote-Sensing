from pathlib import Path
from shutil import copy2

from ReadImage import get_result_image_paths


DEFAULT_IMAGE_COUNT = 2000


def extract_image_paths(folder_path, start_index, skip_count=0, image_count=DEFAULT_IMAGE_COUNT):
    if image_count <= 0:
        raise ValueError(f"image_count must be positive, got {image_count}")
    if start_index < 0:
        raise ValueError(f"start_index must not be negative, got {start_index}")

    result_image_paths = get_result_image_paths(folder_path, skip_count=skip_count)

    if start_index >= len(result_image_paths):
        raise IndexError(
            f"start_index is out of range, start_index={start_index}, "
            f"results length={len(result_image_paths)}"
        )

    end_index = min(start_index + image_count, len(result_image_paths))
    return result_image_paths[start_index:end_index]


def create_unique_output_folder(output_root, folder_name):
    output_root_path = Path(output_root)
    output_folder = output_root_path / folder_name

    if not output_folder.exists():
        output_folder.mkdir(parents=True)
        return output_folder

    suffix = 1
    while True:
        candidate = output_root_path / f"{folder_name}_{suffix}"
        if not candidate.exists():
            candidate.mkdir(parents=True)
            return candidate
        suffix += 1


def copy_image_segment(
    folder_path,
    start_index,
    result_name,
    skip_count=0,
    image_count=DEFAULT_IMAGE_COUNT,
    output_root="extracted_images",
):
    selected_paths = extract_image_paths(
        folder_path,
        start_index=start_index,
        skip_count=skip_count,
        image_count=image_count,
    )

    end_index = start_index + len(selected_paths) - 1
    output_folder = create_unique_output_folder(
        output_root,
        f"{result_name}_images_{start_index}_{end_index}",
    )

    for image_path in selected_paths:
        copy2(image_path, output_folder / image_path.name)

    return selected_paths, output_folder


def copy_image_segments(
    image_sources,
    start_index,
    skip_count=0,
    image_count=DEFAULT_IMAGE_COUNT,
):
    copied_segments = {}

    for result_name, config in image_sources.items():
        selected_paths, output_folder = copy_image_segment(
            config["source_folder"],
            start_index=start_index,
            result_name=result_name,
            skip_count=skip_count,
            image_count=image_count,
            output_root=config["output_root"],
        )
        copied_segments[result_name] = {
            "selected_paths": selected_paths,
            "output_folder": output_folder,
        }

    return copied_segments


def prompt_and_copy_image_segments(
    image_sources,
    skip_count=0,
    image_count=DEFAULT_IMAGE_COUNT,
):
    while True:
        raw_start_index = input(
            "Enter image_results start index for cam1 and cam2, "
            "or press Enter to skip: "
        ).strip()
        if not raw_start_index:
            return

        try:
            start_index = int(raw_start_index)
            copied_segments = copy_image_segments(
                image_sources,
                start_index=start_index,
                skip_count=skip_count,
                image_count=image_count,
            )
        except (ValueError, IndexError) as error:
            print(error)
            continue

        for result_name, copied_segment in copied_segments.items():
            selected_paths = copied_segment["selected_paths"]
            output_folder = copied_segment["output_folder"]
            print(
                f"Copied {len(selected_paths)} images from {result_name} to {output_folder}"
            )

        return {
            "start_index": start_index,
            "copied_segments": copied_segments,
        }
