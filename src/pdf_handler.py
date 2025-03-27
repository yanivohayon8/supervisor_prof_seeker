import re
import pymupdf

def remove_new_line_(text):
    return text.replace("\n"," .")

def remove_citation_(text:str):
    return re.sub("\[\d+\]","",text)

def remove_references_(text:str):
    return re.sub("(References)\s?\n*.*","",text,flags=re.DOTALL|re.IGNORECASE)

def clean_(text:str):
    text = remove_new_line_(text)
    text = remove_citation_(text)
    text = remove_references_(text)
    text = text.strip()

    return text 

def read_pdf_text_(input_path):
    text = None

    with pymupdf.open(input_path) as doc:
        text = chr(12).join([page.get_text() for page in doc])
    
    return text

def read_pdf(input_path):
    text = read_pdf_text_(input_path)
    text = clean_(text)

    return text

def extract_absract(text):
    abstract = re.search("(Abstract|ABSTRACT|A B S T R A C T)(.+)(Introduction|INTRODUCTION)",text,flags=re.DOTALL).group()
    abstract = abstract[:len(abstract)-len("Introduction")]

    return abstract