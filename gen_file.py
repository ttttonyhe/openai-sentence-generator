import re
import json
import types
import random
import pandas as pd
from jinja2 import Template

from constants import *
from generate_value import random_value
from generate_helpers import (
    read_generated_property_values_workbook,
    read_sentences_textfile,
)
from gen_helpers import (
    task_config,
    sample_sentences,
    random_sample_ordered,
    read_templates_workbook,
    save_gen_result_to_workbook,
)
from gen_text_tpl import property_list_tpl, PROPERTY_LIST_STYLE_COUNT

function_names = types.SimpleNamespace()
function_names.text2json_equal = TEXT2JSON_EQUAL_FUNCTION_NAME
function_names.text2json_reduce = TEXT2JSON_REDUCE_FUNCTION_NAME
function_names.json2json_reduce_by_name = JSON2JSON_REDUCE_BY_NAME_FUNCTION_NAME
function_names.json2json_reduce_by_json = JSON2JSON_REDUCE_BY_JSON_FUNCTION_NAME
function_names.text2table_equal = TEXT2TABLE_EQUAL_FUNCTION_NAME
function_names.text2table_reduce = TEXT2TABLE_REDUCE_FUNCTION_NAME


def qa_generator(
    generate_qa_content,
    sentences,
    generated_property_values,
    human_template,
    bot_template,
    sentence_count,
    is_random_property_reduced=False,
    *args,
):
    if not human_template or not bot_template:
        raise ValueError("Human and bot templates must be provided")

    human_tpl = Template(human_template)
    bot_tpl = Template(bot_template)
    result = {"human": [], "bot": []}

    # Define QA generation function
    def generate_qa(remaining_sentences=sentence_count):
        candidate_sentences = sample_sentences(sentences, remaining_sentences)
        for sentence in candidate_sentences:
            if "{{" not in sentence or "}}" not in sentence:
                continue

            property_names = []
            property_values = {}

            # Extract property names from sentence
            for match in re.finditer(r"{{(.*?)}}", sentence):
                property_names.append(match.group(1))

            if len(property_names) == 0:
                continue

            # Shuffle property names
            random.shuffle(property_names)

            for property_idx, property_name in enumerate(property_names):
                property_value, _ = random_value(
                    property_name,
                    generated_property_values,
                    offline=True,
                    ignore_units=False,
                )
                property_values[property_name] = str(property_value)

                # Replace property names with their values in the sentence
                sentence = sentence.replace(
                    f"{{{{{property_name}}}}}", property_values[property_name]
                )

            human, bot = generate_qa_content(
                sentence,
                property_names,
                property_values,
                human_tpl,
                bot_tpl,
                is_random_property_reduced,
                *args,
            )

            if human and bot:
                result["human"].append(human)
                result["bot"].append(bot)

    # Ensure sentence_count amount of QAs are generated
    while len(result["human"]) < sentence_count:
        generate_qa(sentence_count - len(result["human"]))

    return result


def gen_text2json(
    sentence,
    property_names,
    property_values,
    human_tpl,
    bot_tpl,
    is_random_property_reduced,
):
    # Generate name_list_str value
    property_list_str = property_list_tpl(
        property_names, random.randint(1, PROPERTY_LIST_STYLE_COUNT)
    )
    human = human_tpl.render(sentence_str=sentence, name_list_str=property_list_str)

    # If required, drop at least 1 property, but not all properties
    if is_random_property_reduced:
        if len(property_names) == 1:
            return None, None

        property_names = random_sample_ordered(
            property_names, random.randint(1, len(property_names) - 1)
        )

    # Generate name_json_str value
    property_value_dict = {}
    for property_name in property_names:
        property_value_dict[property_name] = property_values[property_name]

    bot = bot_tpl.render(
        name_json_str=json.dumps(property_value_dict, indent=4, ensure_ascii=False)
    )

    return human, bot


def gen_json2json(
    sentence,
    property_names,
    property_values,
    human_tpl,
    bot_tpl,
    is_random_property_reduced=True,
    by_name=False,
):
    property_value_dict = {}
    for property_name in property_names:
        property_value_dict[property_name] = property_values[property_name]

    # Generate source_json_str value
    source_json_str = json.dumps(property_value_dict, indent=4, ensure_ascii=False)

    # If required, drop at least 1 property, but not all properties
    if is_random_property_reduced:
        if len(property_names) == 1:
            return None, None

        property_names = random_sample_ordered(
            property_names, random.randint(1, len(property_names) - 1)
        )

    # Generate target_name_str value
    # By JSON
    target_name_str = json.dumps(
        {key: "" for key in property_names}, indent=4, ensure_ascii=False
    )

    # By Name
    if by_name:
        target_name_str = property_list_tpl(
            property_names, random.randint(1, PROPERTY_LIST_STYLE_COUNT)
        )

    human = human_tpl.render(
        source_json_str=source_json_str, target_name_str=target_name_str
    )

    # Generate name_json_str value
    property_value_dict = {key: property_value_dict[key] for key in property_names}

    bot = bot_tpl.render(
        name_json_str=json.dumps(property_value_dict, indent=4, ensure_ascii=False)
    )

    return human, bot


# Task delegator --------------------------------------------


def gen(config):
    """
    Delegate execution to task-specific function based on task config
    """

    sentences = read_sentences_textfile()
    generated_property_values = read_generated_property_values_workbook()
    templates = read_templates_workbook(config)

    for idx, human_template, bot_template, functions in templates:
        for function in functions:
            result = {}

            match function:
                case function_names.text2json_equal:
                    result = qa_generator(
                        gen_text2json,
                        sentences,
                        generated_property_values,
                        human_template,
                        bot_template,
                        TEXT2JSON_EQUAL_LIMIT,
                        False,
                    )
                case function_names.text2json_reduce:
                    result = qa_generator(
                        gen_text2json,
                        sentences,
                        generated_property_values,
                        human_template,
                        bot_template,
                        TEXT2JSON_REDUCE_LIMIT,
                        True,
                    )
                case function_names.json2json_reduce_by_name:
                    result = qa_generator(
                        gen_json2json,
                        sentences,
                        generated_property_values,
                        human_template,
                        bot_template,
                        JSON2JSON_REDUCE_BY_NAME_LIMIT,
                        True,
                        True,
                    )
                case function_names.json2json_reduce_by_json:
                    result = qa_generator(
                        gen_json2json,
                        sentences,
                        generated_property_values,
                        human_template,
                        bot_template,
                        JSON2JSON_REDUCE_BY_JSON_LIMIT,
                        True,
                        False,
                    )

            if (
                function
                and result
                and len(result["human"]) > 0
                and len(result["bot"]) > 0
            ):
                save_gen_result_to_workbook(result, f"{function}.xlsx")


# Main --------------------------------------------

task_types = ["text2json", "json2json", "text2table"]
task_type_prompt = (
    f"=> Choose which type of QAs you want to generate: ({', '.join(task_types)})\n"
)
task_type = input(task_type_prompt)

if task_type not in task_types:
    raise ValueError(f"Invalid task type: {task_type}")

# Ask to confirm placement of templates workbook
config = task_config(task_type)
templates_workbook_path = config["templates_workbook_path"]
confirmation = input(
    f"=> Have you placed a templates workbook at {templates_workbook_path}? [y/n]\n"
)

if confirmation != "y":
    raise ValueError("Please place a templates workbook in the correct location")

gen(config)
