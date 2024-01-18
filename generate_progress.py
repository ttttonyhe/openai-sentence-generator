from constants import *
from generate_helpers import read_used_properties

used_properties = read_used_properties()

print(
    "Total number of properties that have been used at least once to generate sentences: ",
    len(used_properties),
)
