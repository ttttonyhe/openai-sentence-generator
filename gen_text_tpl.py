PROPERTY_LIST_STYLE_COUNT = 3


def property_list_tpl(properties, style=1):
    if style < 0 or style > PROPERTY_LIST_STYLE_COUNT:
        raise ValueError(f"Invalid style choice: {style}")

    property_list_str = ""

    for property_idx, property_name in enumerate(properties):
        match style:
            case 1:
                property_list_str += f"{property_idx + 1}. {property_name}\n"
            case 2:
                property_list_str += f"{property_name},"
            case 3:
                property_list_str += f"- {property_name}\n"

    # Remove trailing newline, comma, etc.
    property_list_str = property_list_str.rstrip(",\n")

    return property_list_str
