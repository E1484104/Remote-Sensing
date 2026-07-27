from pathlib import Path


def parse_float(value):
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def first_numeric_value(cells):
    for cell in cells:
        value = parse_float(cell)
        if value is not None:
            return value
    return None


def read_lvm_x_values(file_path):
    lvm_path = Path(file_path)

    if not lvm_path.exists():
        raise FileNotFoundError(f"LVM file does not exist: {lvm_path}")
    if not lvm_path.is_file():
        raise IsADirectoryError(f"Path is not a file: {lvm_path}")

    values = []
    in_data_table = False
    x_value_index = None

    with lvm_path.open("r", encoding="utf-8-sig") as lvm_file:
        for raw_line in lvm_file:
            line = raw_line.rstrip("\r\n")
            cells = line.split("\t")
            first_cell = cells[0].strip() if cells else ""

            if first_cell == "X_Value":
                headers = []
                for cell in cells:
                    headers.append(cell.strip())
                x_value_index = headers.index("X_Value")
                in_data_table = True
                continue

            if not in_data_table:
                continue

            if first_cell in {"Channels", "***End_of_Header***"}:
                in_data_table = False
                x_value_index = None
                continue

            if not line.strip():
                continue

            value = None
            if x_value_index is not None and x_value_index < len(cells):
                value = parse_float(cells[x_value_index])

            if value is None:
                value = first_numeric_value(cells)

            if value is not None:
                values.append(value)

    return values


def read_lvms(file_path):
    values = read_lvm_x_values(file_path)
    return values
