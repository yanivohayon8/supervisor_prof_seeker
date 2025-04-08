from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter
from langchain_core.vectorstores import InMemoryVectorStore,VectorStore
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from src import pdf_handler
from src.utils import load_json_settings
from src.api_utils import init_embeddings
import os
from src.vector_store_loaders.faiss_loader import load_vector_store,init_faiss
import json
from glob import glob
from tqdm import tqdm

class PapersMetadataRetriever():

    def __init__(self,root_dir):
        self.root_dir = root_dir # "data/google_scholar/**/*.pdf"
        self.authors_details_paths = [path for path in glob(os.path.join(self.root_dir,"**","author_details.json"))]
        # if you find any other useful source add it here....(profile.json does not seem to be useful now...) 

    def get_supervisors_metadata(self):
        for supervisor_folder in glob(os.path.join(self.root_dir,"*")):
            supervisor_metadata = self.get_metadata_(supervisor_folder)

            if supervisor_metadata:
                yield self.process_metadata_(supervisor_folder,supervisor_metadata)
    
    def get_metadata_(self,supervisor_folder:str):
        try:
            with open(os.path.join(supervisor_folder,"author_details.json"),"r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def process_metadata_(self,supervisor_folder:str,supervisor_metadata:dict):
        supervisor_metadata["supervisor_name"] = supervisor_metadata.get("author").get("name")
        available_pdfs = list()

        for paper_path in glob(os.path.join(supervisor_folder,"papers","*.pdf")):
            file_name = os.path.basename(paper_path)
            article_index = int(file_name.split("_")[0])

            available_pdfs.append({
                "path":paper_path,
                "article_index":article_index,
                **supervisor_metadata["articles"][article_index]
            })
        
        supervisor_metadata["available_pdfs"] = available_pdfs

        return supervisor_metadata



def get_supervisor_brief(name:str, affilations:str, interests:list[str],website:str=None)->str:
    intro_txt = f"{name} is a M.Sc. and Ph.D. supervisor at {affilations}"

    if len(interests) != 0:
        interests_str = ""

        if len(interests) == 1:
            interests_str = interests[0]
        else:
            interests_str = ", ".join(interests[:-1]) + f", and {interests[-1]}"

        final_txt = f"{intro_txt}, with research interests in {interests_str}. "
    else:
        final_txt = intro_txt+". "

    if not website:
        return final_txt
    
    return final_txt + f"More information is available on the supervisor's personal site at {website}."


def get_paper_overview(supervisor_name:str, title:str, publication:str, year,authors:str,num_cites:int):    
    context = (
        f"{supervisor_name} is a co-author of the paper titled \"{title}\", "
        f"published in {publication} in {year}. "
        f"The full list of authors includes: {authors}. "
    )

    try:
        if num_cites>0:
            context = context +f"As of April 2025, the work has been cited {num_cites} times. "
    except Exception as e:
        pass

    return context


class IndexingPipeline():

    def __init__(self,config_path="src/indexing_pipeline/config.json",override_settings:dict=None,metadata_retriever:PapersMetadataRetriever=None):
        self.metadata_retriever = metadata_retriever
        
        self.config_path = config_path
        self.total_settings = load_json_settings(config_path,override_settings=override_settings)

        self.text_splitter_settings = self.total_settings.get("text_splitter",{})
        self.init_text_splitter_()
        
        self.embeddings_settings = self.total_settings.get("embedding",{})
        embedding_type = self.embeddings_settings.pop("type",None)
        self.embeddings = init_embeddings(embedding_type,self.embeddings_settings)

        self.init_vector_store_()

        self.failed_papers_erros = []
        self.succeed_papers = []
 
    def init_text_splitter_(self):
        supported_splitters = {
            "RecursiveCharacterTextSplitter": RecursiveCharacterTextSplitter,
        }

        spliter_type = self.text_splitter_settings.get("type","RecursiveCharacterTextSplitter") #
        
        if  not spliter_type in supported_splitters:
            raise NotImplementedError(f"Currently, Pipeline do not support {spliter_type} text splitter")

        self.text_splitter_settings.pop("type",None)
        self.text_splitter = supported_splitters[spliter_type](**self.text_splitter_settings)

    def init_vector_store_(self):
        self.vector_store_settings  = self.total_settings.get("vector_store")
        vector_store_type = self.vector_store_settings.pop("type","InMemoryVectorStore") 
        
        if vector_store_type == "InMemoryVectorStore":
            self.vector_store = InMemoryVectorStore(self.embeddings)
        elif vector_store_type == "FAISS":
            input_folder = self.vector_store_settings.get("input_folder",None)

            if input_folder and os.path.exists(input_folder):
                self.vector_store = load_vector_store(self.embeddings,self.vector_store_settings)
            else:
                # settings.pop("type",None)
                self.vector_store = init_faiss(self.embeddings)
                
        else:
            raise NotImplementedError(f"Currently, Pipeline does not support vector store {vector_store_type}")

    def save_indxing_(self):
        if isinstance(self.vector_store,FAISS):
            save_folder = self.vector_store_settings.get("save_folder",None)

            if save_folder:
                self.vector_store.save_local(save_folder)

    def run(self):
        if self.metadata_retriever is None:
            raise ValueError("Please set self.metadata_retriever in the constructor")

        for supervisor_metadata in self.metadata_retriever.get_supervisors_metadata():
            self.index_supervisor(supervisor_metadata)

        self.save_indxing_()

    def index_supervisor(self,supervisor_metadata:dict):
        supervisor_name = supervisor_metadata.get("supervisor_name")
        print(f"Indexing the papers of {supervisor_name} (supervisor)")
        self.index_supervisor_brief_(supervisor_metadata)

        for paper_metadata in tqdm(supervisor_metadata["available_pdfs"]):
            doc_metadata = {
                "supervisor_name":supervisor_name,
                "path":paper_metadata["path"]
            }

            self.index_paper_(paper_metadata["path"],supervisor_name,paper_metadata,doc_metadata=doc_metadata)
            
       
    def index_supervisor_brief_(self,supervisor_metadata:dict,doc_metadata:dict={}):
        name = supervisor_metadata.get("supervisor_name")
        author = supervisor_metadata.get("author")
        affilations = author.get("affiliations","Unknown affilations")
        interests = [interest.get("title") for interest in author.get("interests")] if author.get("interests") else list()
        website = author.get("website")

        brief = get_supervisor_brief(name,affilations,interests,website)
        self.vector_store.add_documents([Document(page_content=brief,**doc_metadata)])

    def index_paper_(self,path:str,supervisor_name:str,paper_metadata:dict,doc_metadata:dict={}):
        overview_text = get_paper_overview(supervisor_name,paper_metadata.get("title"),
                                                paper_metadata.get("publication"), paper_metadata.get("year"),
                                                paper_metadata.get("authors"),paper_metadata.get("cited_by").get("value"))
        
        try:
            paper_text = pdf_handler.read_pdf(path)
            abstract_text = pdf_handler.extract_absract(paper_text)

            page_content = (
                f"{overview_text} The abstract below summarizes the paper’s main contributions and findings.\n\n"
                f"{abstract_text}"
            ) 
            
            self.vector_store.add_documents([Document(page_content=page_content,**doc_metadata)])
            self.succeed_papers.append(
                {
                    "path":path,
                }
            )
        except Exception as e:
            self.failed_papers_erros.append(
                {
                    "path":path,
                    "exception": e,
                }
            )

    def print_summary(self):
        num_suc = len(self.succeed_papers)
        num_failed = len(self.failed_papers_erros)
        num_total = num_suc+num_failed
        print(f"Succeed to index {(100*num_suc/num_total):.2f} ({num_suc}/{num_total}) of the papers")


