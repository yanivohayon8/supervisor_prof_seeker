from src.indexing_pipeline.indexing_pipeline import IndexingPipeline,PapersMetadataRetriever
from src.consts import PAPERS_FOLDER

if __name__ == "__main__":
    metadata_retriever = PapersMetadataRetriever(PAPERS_FOLDER)
    indx_pipeline = IndexingPipeline(metadata_retriever=metadata_retriever)
    indx_pipeline.run()
    indx_pipeline.print_summary()