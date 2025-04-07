from src.indexing_pipeline.indexing_pipeline import IndexingPipeline,PapersMetadataRetriever
from glob import glob 

if __name__ == "__main__":
    metadata_retriever = PapersMetadataRetriever("data/google_scholar")
    indx_pipeline = IndexingPipeline()
    indx_pipeline.run()
    