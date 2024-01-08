import os
import re
import pickle
import openpyxl
import pandas as pd

from constants import *

# Exceptions --------------------------------------


class GroupHashAlreadyUsedException(Exception):
    pass


# String manipulation -----------------------------


def compress_newlines(text):
    return re.sub(r"\n+", "\n", text)


def strip_whitespaces(text):
    return re.sub(r"\s+", "", text)


# I/O --------------------------------------------


def read_properties_workbook():
    worksheet = {}

    if not os.path.isfile(PROPERTIES_WORKBOOK_FILE):
        return worksheet

    wb = openpyxl.load_workbook(PROPERTIES_WORKBOOK_FILE)
    ws = wb.active

    for row in ws.rows:
        if row[0].value is None:
            continue
        worksheet[row[0].value] = row[1].value if len(row) > 1 else None

    return worksheet


def read_generated_property_values_workbook():
    property_values = {}

    if not os.path.isfile(GENERATED_PROPERTY_VALUES_FILE):
        return property_values

    wb = openpyxl.load_workbook(GENERATED_PROPERTY_VALUES_FILE)
    ws = wb.active

    for col in ws.columns:
        property_values[col[0].value] = [row.value for row in col[1:]]

    if DEBUGGING:
        print(" => Previously generated property values: ", property_values)

    return property_values


def read_used_group_hashes():
    used_group_hashes = []

    if not os.path.isfile(USED_GROUP_HASHES_FILE):
        return used_group_hashes

    with open(USED_GROUP_HASHES_FILE, "r") as f:
        used_group_hashes = [int(line.strip()) for line in f.readlines()]

    if DEBUGGING:
        print(" => Previously used group hashes: ", used_group_hashes)

    return used_group_hashes


def read_used_properties():
    used_properties = set()

    if not os.path.isfile(USED_PROPERTIES_FILE):
        return used_properties

    with open(USED_PROPERTIES_FILE, "rb") as f:
        used_properties = pickle.load(f)

    if DEBUGGING:
        print(" => Previously used properties: ", used_properties)

    return used_properties


def save_sentences_to_textfile(sentences):
    with open(SENTENCES_TEXT_FILE, "a") as f:
        for sentence in sentences:
            if sentence.strip() == "":
                continue
            f.write(sentence + "\n")


def save_generated_property_values_to_workbook(property_values):
    print(" => Saving generated property values to file...")
    writer = pd.ExcelWriter(GENERATED_PROPERTY_VALUES_FILE)

    # In the same sheet, save each key of the property_values dict as the first row of a column, and the values as the rest of the column
    df = pd.DataFrame(property_values)
    df.to_excel(writer, index=False)

    writer._save()


def save_used_group_hashes_to_file(used_group_hashes):
    print(" => Saving used group hashes to file...")
    with open(USED_GROUP_HASHES_FILE, "w") as f:
        for group_hash in used_group_hashes:
            f.write(str(group_hash) + "\n")


def save_used_properties_to_file(used_properties):
    print(" => Saving used properties to file...")
    with open(USED_PROPERTIES_FILE, "wb") as f:
        pickle.dump(used_properties, f)
