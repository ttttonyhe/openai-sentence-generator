import os
import sys
import random
import openpyxl
import traceback
import pandas as pd

from constants import *
from openai import OpenAI
from dotenv import load_dotenv
from openlimit import ChatRateLimiter
from helpers import strip_whitespaces, compress_newlines
from generate_value import random_value

load_dotenv()

MAX_NUMBER_OF_GENERATIONS = 5

PROMPT_SYSTEM_MESSAGE = """
你将被提供一组属性信息，你的任务是尽你的最大可能以各种不同的形式把这组属性组装成 3 句句式多样并尽可能连贯的话。在你的回答中除了生成的句子外请不要包含任何其他的内容。
"""
PROMPT_EXAMPLE_USER_MESSAGE = """
姓名: 张三, 年龄: 20, 生日: 1990-05-04
"""
PROMPT_EXAMPLE_ASSISTANT_MESSAGE = """
1. 我的姓名是张三，今年 20 岁，出生在 1990 年 5 月 4 日，很高兴认识大家。\n\n
2. 我叫张三，今年已经 20 岁了，我出生在 1990 年 5 月 4 日。\n\n
3. 张三是我的名字，我出生在 1990 年 5 月 4 日，今年 20 岁。
"""

PROPERTY_GROUP_LENGTH_LOWER_BOUND = 5
PROPERTY_GROUP_LENGTH_UPPER_BOUND = 10

rate_limiter = ChatRateLimiter(request_limit=GPT_RPM, token_limit=GPT_TPM)
openai_client = OpenAI()

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
        worksheet[row[0].value] = row[1].value

    return worksheet


def read_generated_property_values_workbook():
    property_values = {}

    if not os.path.isfile(GENERATED_PROPERTY_VALUES_FILE):
        return property_values

    wb = openpyxl.load_workbook(GENERATED_PROPERTY_VALUES_FILE)

    for sheet in wb.sheetnames:
        property_values[sheet] = [cell.value for cell in wb[sheet]["A"][1:]]

    print("Previously generated property values: ", property_values)

    return property_values


def read_used_group_hashes():
    used_group_hashes = []

    if not os.path.isfile(USED_GROUP_HASHES_FILE):
        return used_group_hashes

    with open(USED_GROUP_HASHES_FILE, "r") as f:
        used_group_hashes = [int(line.strip()) for line in f.readlines()]

    print("Previously used group hashes: ", used_group_hashes)

    return used_group_hashes


def save_sentences_to_textfile(sentences):
    with open(SENTENCES_TEXT_FILE, "a") as f:
        for sentence in sentences:
            f.write(sentence + "\n")


def save_generated_property_values_to_workbook(property_values):
    print("Saving generated property values to file...")
    writer = pd.ExcelWriter(GENERATED_PROPERTY_VALUES_FILE)

    for col, values in property_values.items():
        df = pd.DataFrame({col: values})
        df.to_excel(writer, sheet_name=col, index=False)

    writer._save()


def save_used_group_hashes_to_file(used_group_hashes):
    print("Saving used group hashes to file...")
    with open(USED_GROUP_HASHES_FILE, "w") as f:
        for group_hash in used_group_hashes:
            f.write(str(group_hash) + "\n")


# Data --------------------------------------------

worksheet = read_properties_workbook()
used_group_hashes = read_used_group_hashes()
generated_property_values = read_generated_property_values_workbook()

# Logic --------------------------------------------


def generate_random_property_group(worksheet, properties):
    group = random.sample(
        properties,
        random.randint(
            PROPERTY_GROUP_LENGTH_LOWER_BOUND, PROPERTY_GROUP_LENGTH_UPPER_BOUND
        ),
    )
    group_hash = hash(tuple(sorted(group)))

    if group_hash in used_group_hashes:
        return generate_random_property_group(worksheet, properties)

    used_group_hashes.append(group_hash)

    return {prop: worksheet[prop] for prop in group}


def generate_property_group_prompt(property_group):
    global generated_property_values
    prompt = ""

    for prop in property_group.items():
        if prop[1] is not None:
            val = prop[1]
        else:
            val, generated_property_values = random_value(
                prop[0], generated_property_values
            )

        prompt += f"{prop[0]}: {str(val).strip()}, "

    prompt = prompt[:-2]

    return prompt


def get_openai_response(prompt):
    openai_params = {
        "model": GPT_MODEL,
        "temperature": GPT_TEMPERATURE,
        "frequency_penalty": GPT_FREQUENCY_PENALTY,
        "messages": [
            # System message
            {"role": "system", "content": PROMPT_SYSTEM_MESSAGE},
            # Example
            {"role": "user", "content": PROMPT_EXAMPLE_USER_MESSAGE},
            {"role": "assistant", "content": PROMPT_EXAMPLE_ASSISTANT_MESSAGE},
            # User message
            {"role": "user", "content": prompt},
        ],
    }

    with rate_limiter.limit(**openai_params):
        response = openai_client.chat.completions.create(**openai_params)

    response_message = response.choices[0]

    if response_message.finish_reason == "stop":
        return response_message.message.content

    return ""


def generate_sentences(worksheet):
    print("# ---------------------------------------------------- #")
    print("# --- Pre-processing --------------------------- #")
    properties = list(worksheet.keys())
    property_group = generate_random_property_group(worksheet, properties)
    prompt = generate_property_group_prompt(property_group)

    print("# --- Main process ----------------------------- #")
    print("Generating sentences from properties: ", prompt)

    response = get_openai_response(prompt)
    sentences = get_sentences_from_openai_response(response, property_group)

    print("# --- Result ----------------------------------- #")
    print("Complete. Sentences: ", sentences)
    print("# ---------------------------------------------------- #")

    return sentences


# Helpers --------------------------------------------


def get_sentences_from_openai_response(response, property_group):
    sentences = compress_newlines(response).split("\n")

    for idx, sentence in enumerate(sentences):
        # remove trailing and leading spaces
        sentence = strip_whitespaces(sentence)

        # remove leading numbers
        if sentence != "" and sentence[0].isdigit():
            sentences[idx] = sentence[3:]

    sentences = list(filter(lambda x: x != "", sentences))

    # templatize sentences
    for idx, sentence in enumerate(sentences):
        for prop in property_group.items():
            sentences[idx] = sentences[idx].replace(
                strip_whitespaces(str(prop[1])), f"{{{{{prop[0]}}}}}"
            )

    return sentences


# Main --------------------------------------------

# Main loop
success_count = 0
while True:
    if MAX_NUMBER_OF_GENERATIONS == 0 or success_count < MAX_NUMBER_OF_GENERATIONS:
        try:
            sentences = generate_sentences(worksheet)
            save_sentences_to_textfile(sentences)
            print("")
            success_count += 1
        except KeyboardInterrupt:
            print("Keyboard interrupted, exiting...")
            break
        except Exception as e:
            traceback.print_exc()
            break
        except:
            print("Rate limit reached or an error has occurred, retrying...")
    else:
        break

# Save transactional data
if generated_property_values:
    save_generated_property_values_to_workbook(generated_property_values)

if used_group_hashes:
    save_used_group_hashes_to_file(used_group_hashes)

sys.exit(0)
