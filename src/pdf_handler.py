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

def extract_absract(text:str,max_num_characters=1500):
    '''
        expected number of character is between 150 to 250
        250 words × 6 characters/word = ~1,500 characters
    '''
    try:
        abstract = re.search("(Abstract|ABSTRACT|A B S T R A C T|a b s t r a c t)(.+)(Introduction|INTRODUCTION)",text,flags=re.DOTALL).group()
        abstract = abstract[:len(abstract)-len("Introduction")]
    except AttributeError as e:
        # Heuristics for the variablity: TODO: make it more accurate
        abstract = re.search("(Abstract|ABSTRACT|A B S T R A C T|a b s t r a c t)(.+)",text,flags=re.DOTALL).group()
        abstract = abstract[:max_num_characters]

    return abstract

def extract_introduction(text:str):
    intro = re.search("(Introduction|INTRODUCTION)(.+)(Related work|Related Work)",text,flags=re.DOTALL).group() # Methods

    return intro