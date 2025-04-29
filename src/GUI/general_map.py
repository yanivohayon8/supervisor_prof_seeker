import streamlit as st
from src.indexing_pipeline.indexing_pipeline import PapersMetadataRetriever

def expander_supervisor_by_interest(metadata_retriever:PapersMetadataRetriever):
    total_interests = metadata_retriever.get_supervisors_by_interests()

    for interest,supervisors_info in total_interests.items():

        with st.expander(interest):
            num_images = len(supervisors_info)
            cols = st.columns(num_images)
            max_width = 300
            min_width = 100
            page_width = 1000  # Estimate of available space
            image_width = max(min_width, min(max_width, page_width // num_images))

            for col, info in zip(cols, supervisors_info):
                with col:
                    st.image(info.get("image"), caption=info.get("name"), width=image_width)

            