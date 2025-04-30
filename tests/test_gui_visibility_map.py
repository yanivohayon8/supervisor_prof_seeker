import streamlit as st
from src.GUI.bird_eye_graph import build_bird_eye_graph_,save_bird_eye_graph,load_bird_eye_graph,load_naive_graph
from src.GUI.general_map import expander_supervisor_by_interest

import os
from src.indexing_pipeline import indexing_pipeline 

def test_build_and_save_graph():
    nodes,edges = build_bird_eye_graph_()
    save_bird_eye_graph("src/GUI/graph_data.json",nodes,edges)

def test_load_graph():
    load_bird_eye_graph("src/GUI/graph_data.json")


def test_two_tabs():
    import time
    import random

    # Simulate dynamic image loading for Tab 1
    def get_image_sets_for_tab():
        time.sleep(0.5)  # simulate load delay
        groups = ["Group A", "Group B", "Group C", "Group D"]
        image_sets = {}
        for group in random.sample(groups, k=random.randint(2, 4)):
            images = {
                f"{group} - Person {i+1}": f"http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png"
                for i in range(random.randint(2, 5))  # multiple images per group
            }
            image_sets[group] = images
        return image_sets

    # Simulate text loading for Tab 2
    def get_text_sections_for_tab(tab_name):
        time.sleep(0.5)
        num_sections = random.randint(3, 5)
        return {
            f"{tab_name} Section {i+1}": f"This is dynamically loaded content for {tab_name} Section {i+1}"
            for i in range(num_sections)
        }

    # Start Streamlit app
    st.title("Dynamic Tabs with Responsive Images in Expanders")

    tab1, tab2 = st.tabs(["Image Gallery (Tab 1)", "Text Content (Tab 2)"])

    # Tab 1: Expanders with multiple images (responsive widths)
    with tab1:
        st.subheader("People Groups")
        image_groups = get_image_sets_for_tab()
        for group_name, images in image_groups.items():
            with st.expander(group_name):
                num_images = len(images)
                cols = st.columns(num_images)
                max_width = 300
                min_width = 100
                page_width = 1000  # Estimate of available space
                image_width = max(min_width, min(max_width, page_width // num_images))
                for col, (caption, img_url) in zip(cols, images.items()):
                    with col:
                        st.image(img_url, caption=caption, width=image_width)

    # Tab 2: Expanders with text
    with tab2:
        st.subheader("Documentation Sections")
        text_data = get_text_sections_for_tab("Tab 2")
        for title, content in text_data.items():
            with st.expander(title):
                st.write(content)

def test_expander_supervisor_by_interest():
    tests_root_folder = os.path.join("tests","data","google_scholar")
    metadata_retriever = indexing_pipeline.PapersMetadataRetriever(tests_root_folder)

    expander_supervisor_by_interest(metadata_retriever)

if __name__ == "__main__":   

    

    # test_build_and_save_graph()
    # test_load_graph()
    # load_naive_graph()

    # test_two_tabs()

    test_expander_supervisor_by_interest()