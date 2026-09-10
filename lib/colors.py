def hex_to_rgb(value: str) -> tuple:
    value = value.lstrip("#").lower()
    if len(value) != 6:
        return (255, 255, 255)

    try:
        return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))
    except ValueError:
        return (255, 255, 255)
