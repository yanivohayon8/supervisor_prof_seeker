import re

def remove_new_line_(text):
    return text.replace("\n"," .")

def remove_references_(text:str):
    return re.sub("\[\d+\]","",text)

def clean_(text:str):
    text = remove_new_line_(text)
    text = remove_references_(text)
    text = text.strip()

    return text 