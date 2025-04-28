# supervisor_prof_seeker
This project is an AI assistant designed to help M.Sc. and Ph.D. students find a suitable research supervisor. The assistant leverages large language models (LLMs) and relies on a knowledge base built from pre-indexed papers and publicly available information. During conversations, it recommends potential researchers and provides detailed information about their work, even for students who may not have expertise in the research domain. This includes specific research areas, motivations, and suggested foundational courses related to the research field.


## Features
* Automated Scraping: Gather published papers from relevant sources.
* Search and Filter: Allow students to search for supervisors by topic, methods, or applications.

<!--## Tech Stack
Python (core language), LangChain, LangGraph, LLMs, streamlit, scrapy, pymupdf-->

## Installation
Create the conda environment:
 ```
    conda env create -f environment.yml
    conda activate supervisor_prof_seeker_03_2025
 ```

Install the other packages with pip:
```
    pip install -r requirements.txt
```

## How to run the code
```
    python -m streamlit run app.py
```

<!--On demand add explanation on how to do the indexing-->