from src.indexing_pipeline.indexing_pipeline import PapersMetadataRetriever
from streamlit_agraph import agraph, Node, Edge, Config
from src.consts import PAPERS_FOLDER
import json

def load_naive_graph():
    nodes = []
    edges = []
    nodes.append( Node(id="Spiderman", 
                    label="Peter Parker", 
                    size=25, 
                    shape="circularImage",
                    image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png") 
                ) # includes **kwargs
    nodes.append( Node(id="Captain_Marvel", 
                    size=25,
                    shape="circularImage",
                    image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_captainmarvel.png") 
                )
    edges.append( Edge(source="Captain_Marvel", 
                    label="friend_of", 
                    target="Spiderman", 
                    # **kwargs
                    ) 
                ) 

    config = Config(width=1000,
                    height=2000,
                    directed=True, 
                    physics=True, 
                    hierarchical=False,
                    # **kwargs
                    )

    return agraph(nodes=nodes, 
                        edges=edges, 
                        config=config)

def build_bird_eye_graph_(node_size = 25, node_shape = "circularImage"):
    metadata_retriever = PapersMetadataRetriever(PAPERS_FOLDER)
    total_interests = set()
    nodes = []
    edges = []

    for supervisor_metadata in metadata_retriever.get_supervisors_metadata():
        author = supervisor_metadata.get("author")
        node_id = supervisor_metadata.get("supervisor_name")

        nodes.append(
            {
                "id":node_id,
                # "label": node_id, #author.get("affiliations","Unknown affilations"),
                # "image": supervisor_metadata.get("image"),
                "size":node_size,
                # "shape":node_shape,
            }
        )

        supervisor_interests = [interest.get("title") for interest in author.get("interests")] if author.get("interests") else list()

        for interest in supervisor_interests:
            if not interest in total_interests:
                total_interests.add(interest)
                nodes.append({
                    "id":interest,
                    # "label":interest,
                    "size":node_size*2,
                    # "shape":node_shape,
                })

        for interest in supervisor_interests:
            edges.append(
                {
                    "source": node_id,
                    # "label": "inte"
                    "target":interest,
                }
            )
    
       
    
    return nodes,edges

def save_bird_eye_graph(file_path:str,nodes:dict,edges:dict):
    graph_data = {
        "nodes":nodes,
        "edges":edges
    }

    with open(file_path,"w") as f:
        json.dump(graph_data,f)

def get_config_params_():
    return {
        "width": 1000,
        "height": 2000, #"100%",#950,
        "directed":True, 
        "physics": True,#True, 
        "hierarchical":False, # False

    }

def load_bird_eye_graph(file_path):
    with open(file_path,"r") as f:
        graph_data = json.load(f)
    
    nodes = [Node(**data) for data in graph_data.get("nodes")]
    edges = [Edge(**data) for data in graph_data.get("edges")]

    
    config = Config(get_config_params_())

    return agraph(nodes=nodes, 
                        edges=edges, 
                        config=config)
    

