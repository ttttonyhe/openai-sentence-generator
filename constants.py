DEBUGGING = False

# OpenAI Sentence Generator
PROPERTIES_WORKBOOK_FILE = "./data/properties.xlsx"
SENTENCES_TEXT_FILE = "./result/sentences.txt"
GENERATED_PROPERTY_VALUES_FILE = "./store/generated_property_values.xlsx"
USED_GROUP_HASHES_FILE = "./store/used_group_hashes.txt"
USED_PROPERTIES_FILE = "./store/used_properties.txt"

GPT_MODEL = "gpt-3.5-turbo"
GPT_TEMPERATURE = 0.8
GPT_FREQUENCY_PENALTY = 0.8
GPT_TPM = 60000
GPT_RPM = 500

# Text2Json
VERBOSE = False

SENTENCES_DATA_TEXT_FILE = "./data/sentences.txt"
TEMPLATES_WORKBOOK_FILE = "./data/templates.xlsx"
TEXT2JSON_WORKBOOK_DIR = "./result"

REQUIRED_COLUMNS = ["human_tpl", "bot_tpl", "function"]
HUMAN_TEMPLATE_STRINGS = ["{{sentence_str}}", "{{name_list_str}}"]
BOT_TEMPLATE_STRINGS = ["{{name_json_str}}"]
EQUAL_FUNCTION_NAME = "text2json_equal"
REDUCE_FUNCTION_NAME = "text2json_reduce"
NUMBER_OF_REDUCED_JSONS = 10
