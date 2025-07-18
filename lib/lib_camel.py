import re

def snake_to_camel(snake_str: str) -> str:
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def dict_to_camel_case(obj):
    if isinstance(obj, list):
        return [dict_to_camel_case(item) for item in obj]
    elif isinstance(obj, dict):
        return {snake_to_camel(k): dict_to_camel_case(v) for k, v in obj.items()}
    else:
        return obj