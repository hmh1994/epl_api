import re

def to_camel_case(snake_str: str) -> str:
    return re.sub(r'_([a-zA-Z])', lambda match: match.group(1).upper(), snake_str)

def dict_to_camel_case(d: dict) -> dict:
    return {to_camel_case(k): v for k, v in d.items()}

