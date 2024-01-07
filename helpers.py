import string
import re

def compress_newlines(text):
    return re.sub(r'\n+', '\n', text)

def strip_whitespaces(text):
    return text.translate({ord(c): None for c in string.whitespace})
