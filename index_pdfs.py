from src.indexing_pipeline.indexing_pipeline import IndexingPipeline
from glob import glob 

if __name__ == "__main__":
    indx_pipeline = IndexingPipeline()

    pdfs = glob("data/**/*.pdf")
    indx_pipeline.run(pdfs)
    