def coerce_to_list(value) -> list:
    if isinstance(value, list):
        return value
    else:
        return [value]
