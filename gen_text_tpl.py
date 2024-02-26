PROPERTY_LIST_STYLE_COUNT = 14


def property_list_tpl(properties, style=1):
    if style < 0 or style > PROPERTY_LIST_STYLE_COUNT:
        raise ValueError(f"Invalid style choice: {style}")

    property_list_str = ""

    for property_idx, property_name in enumerate(properties):
        match style:
            case 1:  # 序号.property_name
                property_list_str += f"{property_idx + 1}. {property_name}\n"
            case 2 | 10:  # (概率up) 英文逗号分割property_name
                property_list_str += f"{property_name},"
            case 3:  # -空格property_name
                property_list_str += f"- {property_name}\n"
            case 4 | 11:  # (概率up) 直接用回车分隔
                property_list_str += f"{property_name}\n"
            case 5 | 12:  # (概率up) 用空格分隔
                property_list_str += f"{property_name} "
            case 6 | 13:  # (概率up) 用tab键分隔
                property_list_str += f"{property_name}\t"
            case 7 | 14:  # (概率up) 用中文的逗号，分隔
                property_list_str += f"{property_name}，"
            case 8:  # 用分号分隔
                property_list_str += f"{property_name};"
            case 9:  # 用中横线-分隔
                property_list_str += f"{property_name}-"
    # Remove trailing newline, comma, etc.
    property_list_str = property_list_str.rstrip(",\n\t，;- ")

    return property_list_str
