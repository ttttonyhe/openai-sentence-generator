import openpyxl
import random

PROPERTIES_WORKBOOK_FILE = "./properties.xlsx"
PROPERTY_GROUP_LENGTH_LOWER_BOUND = 5
PROPERTY_GROUP_LENGTH_UPPER_BOUND = 10

PROPERTY_DUPLICATION_THRESHOLD = 5

PROMPT_SYSTEM_MESSAGE = """
你将被提供多组属性信息，你的任务是尽你的最大可能以各种不同的形式把每组属性组装成3句句式多样并尽可能连贯的话。如果属性值未知，你可以随即生成一个合适的值。
"""


def read_workbook():
    worksheet = {}

    wb = openpyxl.load_workbook(PROPERTIES_WORKBOOK_FILE)
    ws = wb.active

    for row in ws.rows:
        if row[0].value is None:
            continue
        worksheet[row[0].value] = row[1].value

    return worksheet


def generate_random_property_group(worksheet, properties):
    props = random.sample(
        properties,
        random.randint(
            PROPERTY_GROUP_LENGTH_LOWER_BOUND, PROPERTY_GROUP_LENGTH_UPPER_BOUND
        ),
    )
    return {prop: worksheet[prop] for prop in props}


def generate_property_group_prompt(property_group):
    prompt = ""

    for prop in property_group.items():
        val = prop[1] if prop[1] is not None else "未知"
        prompt += f"{prop[0]}: {val}, "

    prompt = prompt[:-2]

    return prompt


def get_openai_response(prompt):
    return


def process_openai_response(response):
    return


worksheet = read_workbook()
properties = list(worksheet.keys())

property_group = generate_random_property_group(worksheet, properties)
prompt = generate_property_group_prompt(property_group)

print(prompt)
