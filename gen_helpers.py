import os
import random
import pandas as pd

from constants import *
from generate_helpers import print_info, strip_whitespaces

# Business logic ------------------------------------------


def task_config(task_type):
    config = {
        "templates_workbook_path": TEXT2JSON_TEMPLATES_WORKBOOK_FILE,
        "human_template_strings": TEXT2JSON_HUMAN_TEMPLATE_STRINGS,
        "bot_template_strings": TEXT2JSON_BOT_TEMPLATE_STRINGS,
    }

    match task_type:
        case "json2json":
            config["templates_workbook_path"] = JSON2JSON_TEMPLATES_WORKBOOK_FILE
            config["human_template_strings"] = JSON2JSON_HUMAN_TEMPLATE_STRINGS
            config["bot_template_strings"] = JSON2JSON_BOT_TEMPLATE_STRINGS
        case "text2table":
            config["templates_workbook_path"] = TEXT2TABLE_TEMPLATES_WORKBOOK_FILE
            config["human_template_strings"] = TEXT2TABLE_HUMAN_TEMPLATE_STRINGS
            config["bot_template_strings"] = TEXT2TABLE_BOT_TEMPLATE_STRINGS

    return config


def sample_sentences(sentences, sample_size):
    candidate_sentences = sentences[:]

    # If not enough sentences available, repeat sentences
    while len(candidate_sentences) < sample_size:
        candidate_sentences.extend(candidate_sentences)

    candidate_sentences = random.sample(candidate_sentences, sample_size)

    return candidate_sentences


def replace_properties_with_aliases(property_value_dict):
    property_aliases = read_property_aliases_workbook()

    for property_name in list(property_value_dict):
        if property_name in property_aliases:
            property_value_dict[property_aliases[property_name]] = property_value_dict[
                property_name
            ]
            del property_value_dict[property_name]

    return property_value_dict


# Patches ----------------------------------------


def random_sample_ordered(source_list, sample_size):
    return [
        source_list[i]
        for i in sorted(random.sample(range(len(source_list)), sample_size))
    ]


# String manipulation -----------------------------


def display_char_count(string):
    total = 0

    for s in strip_whitespaces(string):
        if "\u4e00" <= s <= "\u9fef":
            total += 3
        elif s.isupper():
            total += 2
        else:
            total += 1

    return total


# I/O --------------------------------------------


def read_templates_workbook(task_config):
    templates = []
    tpl_df = pd.read_excel(task_config["templates_workbook_path"])

    if not all(column in tpl_df.columns for column in REQUIRED_COLUMNS):
        raise ValueError("One or more required columns are missing")

    for idx, row in tpl_df.iterrows():
        if not all(
            tpl_str in row["human_tpl"]
            for tpl_str in task_config["human_template_strings"]
        ):
            raise ValueError(f"Human template string is missing from row {idx}")

        if not all(
            tpl_str in row["bot_tpl"] for tpl_str in task_config["bot_template_strings"]
        ):
            raise ValueError(f"Bot template string is missing from row {idx}")

        functions = strip_whitespaces(row["function"]).split(",")
        if len(functions) == 0:
            raise ValueError(f"Function is missing from row {idx}")

        row_tuple = (idx, row["human_tpl"], row["bot_tpl"], functions)
        templates.append(row_tuple)

    if DEBUGGING:
        print_info(" => Templates: ", templates)

    return templates


def read_property_aliases_workbook():
    property_aliases = {}
    pa_df = pd.read_excel(PROPERTY_ALIASES_WORKBOOK_FILE)

    for idx, row in pa_df.iterrows():
        property_aliases[row["name"]] = row["alias"]

    if DEBUGGING:
        print_info(" => Property aliases: ", property_aliases)

    return property_aliases


def save_gen_result_to_workbook(result, filename):
    print_info(f" => Saving generated human-bot QAs to file {filename}...")
    workbook_path = f"{GEN_FILE_WORKBOOK_DIR}/{filename}"

    old_df = pd.DataFrame(columns=["human", "bot"])
    if os.path.exists(workbook_path):
        old_df = pd.read_excel(workbook_path)

    new_df = pd.DataFrame(result)
    df = pd.concat([old_df, new_df])

    df.to_excel(workbook_path, index=False)
