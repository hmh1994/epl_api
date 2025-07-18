import re

def snake_to_camel(snake_str: str) -> str:
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def dict_to_camel_case(snake_dict: dict) -> dict:
    return {snake_to_camel(k): v for k, v in snake_dict.items()}

def dict_to_camel_case_obj(obj):
    if isinstance(obj, list):
        return [dict_to_camel_case(item) for item in obj]
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_obj[to_camel_case(k)] = dict_to_camel_case(v)
        return new_obj
    else:
        return obj