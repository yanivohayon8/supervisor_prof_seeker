import re

def remove_new_line_(text):
    return text.replace("\n"," .")

def clean_(text:str):
    text = remove_new_line_(text)
    text = text.strip()

    return text 