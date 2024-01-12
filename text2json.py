import re
import json
import random
import pandas as pd

from constants import *
from generate_value import random_value
from helpers import (
    read_templates_workbook,
    read_generated_property_values_workbook,
    read_sentences_textfile,
    save_sentences_jsons_to_workbook,
)


def sentences2jsons(
    sentences,
    generated_property_values,
    human_template,
    bot_template,
    random_property_reduction=False,
):
    if not human_template or not bot_template:
        raise ValueError("Human and bot templates must be provided")

    sentences_jsons = {"human": [], "bot": []}

    for sentence in sentences:
        if "{{" not in sentence or "}}" not in sentence:
            continue

        property_names = []
        property_values = {}

        # Extract property names from sentence
        for match in re.finditer(r"{{(.*?)}}", sentence):
            property_names.append(match.group(1))

        # Generate name_list_str value
        property_list_str = ""
        for property_idx, property_name in enumerate(property_names):
            property_value, _ = random_value(
                property_name, generated_property_values, True
            )
            property_values[property_name] = property_value
            property_list_str += (
                f"{property_idx + 1}. {property_name}: {property_value}\n"
            )

            # Replace property names with values in sentence
            sentence = sentence.replace(
                f"{{{{{property_name}}}}}", property_values[property_name]
            )

        human = human_template.replace("{{sentence_str}}", sentence)
        human = human.replace("{{name_list_str}}", property_list_str.strip())

        # Drop at least 1 property, but not all properties
        if random_property_reduction:
            property_names = random.sample(
                property_names, random.randint(1, len(property_names) - 1)
            )

        # Generate name_json_str value
        property_value_dict = {}
        for property_name in property_names:
            property_value_dict[property_name] = property_values[property_name]

        bot = bot_template.replace(
            "{{name_json_str}}",
            json.dumps(property_value_dict, indent=4, ensure_ascii=False),
        )

        sentences_jsons["human"].append(human)
        sentences_jsons["bot"].append(bot)

    return sentences_jsons


def text2json_equal(sentences):
    return sentences2jsons(
        sentences,
        generated_property_values,
        human_template,
        bot_template,
        False,
    )


def text2json_reduce(sentences, sentence_count=NUMBER_OF_REDUCED_JSONS):
    candidate_sentences = sentences[:]

    # If not enough sentences available, repeat sentences
    while len(candidate_sentences) < sentence_count:
        candidate_sentences.extend(candidate_sentences)

    candidate_sentences = random.sample(candidate_sentences, sentence_count)

    return sentences2jsons(
        candidate_sentences,
        generated_property_values,
        human_template,
        bot_template,
        True,
    )


# --------------------------------------------

sentences = read_sentences_textfile()
generated_property_values = read_generated_property_values_workbook()
templates = read_templates_workbook()


for idx, human_template, bot_template, functions in templates:
    for function in functions:
        function_name = "equal"
        sentences_jsons = {}

        if function == EQUAL_FUNCTION_NAME:
            function_name = "equal"
            sentences_jsons = text2json_equal(sentences)
        elif function == REDUCE_FUNCTION_NAME:
            function_name = "reduce"
            sentences_jsons = text2json_reduce(sentences)

        if (
            sentences_jsons
            and len(sentences_jsons["human"]) > 0
            and len(sentences_jsons["bot"]) > 0
        ):
            save_sentences_jsons_to_workbook(
                sentences_jsons, f"{idx}_{function_name}.xlsx"
            )
