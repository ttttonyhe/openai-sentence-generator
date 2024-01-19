DEBUGGING = False

# OpenAI Sentence Generator ----------------------
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

# Human-Bot QA Generator -------------------------
VERBOSE = False
REQUIRED_COLUMNS = ["human_tpl", "bot_tpl", "function"]

SENTENCES_DATA_TEXT_FILE = "./data/sentences.txt"
PROPERTY_ALIASES_WORKBOOK_FILE = "./data/property_aliases.xlsx"
TEXT2JSON_TEMPLATES_WORKBOOK_FILE = "./data/text2json_templates.xlsx"
JSON2JSON_TEMPLATES_WORKBOOK_FILE = "./data/json2json_templates.xlsx"
TEXT2TABLE_TEMPLATES_WORKBOOK_FILE = "./data/text2table_templates.xlsx"
GEN_FILE_WORKBOOK_DIR = "./result"

# 是否在回答中使用属性别名
USE_PROPERTY_ALIASES = True

# Text2JSON -------------------
TEXT2JSON_HUMAN_TEMPLATE_STRINGS = ["{{sentence_str}}", "{{name_list_str}}"]
TEXT2JSON_BOT_TEMPLATE_STRINGS = ["{{name_json_str}}"]
TEXT2JSON_EQUAL_FUNCTION_NAME = "text2json_equal"
TEXT2JSON_REDUCE_FUNCTION_NAME = "text2json_reduce"

# 配置每个用例的生成上限
TEXT2JSON_EQUAL_LIMIT = 2
TEXT2JSON_REDUCE_LIMIT = 3

# JSON2JSON -------------------
JSON2JSON_REDUCE_BY_NAME_FUNCTION_NAME = "json2json_reduce_by_name"
JSON2JSON_REDUCE_BY_JSON_FUNCTION_NAME = "json2json_reduce_by_json"
JSON2JSON_HUMAN_TEMPLATE_STRINGS = ["{{source_json_str}}", "{{target_name_str}}"]
JSON2JSON_BOT_TEMPLATE_STRINGS = ["{{name_json_str}}"]

# 配置每个用例的生成上限
JSON2JSON_REDUCE_BY_NAME_LIMIT = 2
JSON2JSON_REDUCE_BY_JSON_LIMIT = 3

# Text2Table ------------------
TEXT2TABLE_EQUAL_FUNCTION_NAME = "text2table_equal"
TEXT2TABLE_EQUAL_MARKDOWN_FUNCTION_NAME = "text2table_equal_markdown"
TEXT2TABLE_REDUCE_FUNCTION_NAME = "text2table_reduce"
TEXT2TABLE_REDUCE_MARKDOWN_FUNCTION_NAME = "text2table_reduce_markdown"
TEXT2TABLE_HUMAN_TEMPLATE_STRINGS = ["{{sentence_str}}", "{{name_list_str}}"]
TEXT2TABLE_BOT_TEMPLATE_STRINGS = ["{{name_table_str}}"]

# 配置每个用例的生成上限
TEXT2TABLE_EQUAL_LIMIT = 2
TEXT2TABLE_REDUCE_LIMIT = 3
