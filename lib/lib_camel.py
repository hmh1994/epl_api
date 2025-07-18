import re

def snake_to_camel(snake_str: str) -> str:
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def dict_to_camel_case(snake_dict: dict) -> dict:
    return {snake_to_camel(k): v for k, v in snake_dict.items()}
