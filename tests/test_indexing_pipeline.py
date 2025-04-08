import unittest
from src.indexing_pipeline import indexing_pipeline 
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import faiss
from langchain_community.docstore import InMemoryDocstore
import shutil
import os
from src import pdf_handler
from glob import glob
from src.consts import PAPERS_FOLDER

tests_root_folder = os.path.join("tests","data","google_scholar")


class TestPOC(unittest.TestCase):

    def index_pdf_paper(self,pdf_path:str,text_splitter,vector_store):
        text = pdf_handler.read_pdf(pdf_path)
        abstract = pdf_handler.extract_absract(text)
        intro = pdf_handler.extract_introduction(text)

        page_content = abstract+ " " + intro

        doc = Document(
            page_content=page_content,
            metadata={
                "sections":["abstract","introduction"],
                "input_file":pdf_path
                }
            )

        docs = [doc]

        all_splits = text_splitter.split_documents(docs)
        vector_store.add_documents(documents=all_splits)

    def test_index_pdf_InMemoryVectorStore(self):
        file_path = "tests/data/Ohad Ben-shahar/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")
        vector_store = InMemoryVectorStore(embeddings)

        self.index_pdf_paper(file_path,text_splitter,vector_store)

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = vector_store.similarity_search(query,k=2)

        self.assertEqual(len(similar_docs),2)

        print(similar_docs)

    def test_index_pdf_faiss_1(self):
        file_path = "tests/data/Ohad Ben-shahar/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
        embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-mpnet-base-v2")
        vector = embeddings.embed_query("hello world")
        index = faiss.IndexFlatL2(len(vector))
        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
            )

        self.index_pdf_paper(file_path,text_splitter,vector_store)

        query = "Ancient artworks are obtained in archaeological excavations."
        similar_docs = vector_store.similarity_search(query,k=2)

        self.assertEqual(len(similar_docs),2)

        print(similar_docs)


class TestPapersMetadataRetriever(unittest.TestCase):

    def test_get_metadata_on_test_data(self):
        metadata_retriever = indexing_pipeline.PapersMetadataRetriever(tests_root_folder)
        count_supervisors = 0

        for supervisor_metadata in metadata_retriever.get_supervisors_metadata():
            count_supervisors+=1
            self.assertIn("available_pdfs",supervisor_metadata.keys())
            self.assertGreater(len(supervisor_metadata["available_pdfs"]),0)

        expected_num_supervisors = len(glob(os.path.join(tests_root_folder,"*")))
        self.assertEqual(expected_num_supervisors,count_supervisors)
    
    def test_get_metadata(self):
        metadata_retriever = indexing_pipeline.PapersMetadataRetriever(PAPERS_FOLDER)
        count_supervisors = 0

        for supervisor_metadata in metadata_retriever.get_supervisors_metadata():
            count_supervisors+=1
            self.assertIn("available_pdfs",supervisor_metadata.keys())

        expected_num_supervisors = len(glob(os.path.join(PAPERS_FOLDER,"*","author_details.json")))
        self.assertEqual(expected_num_supervisors,count_supervisors)

class TestPipeline(unittest.TestCase):

    paper_metadata = {
            "title": "Pictorial and apictorial polygonal jigsaw puzzles from arbitrary number of crossing cuts",
            "link": "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=t77PmuQAAAAJ&pagesize=100&citation_for_view=t77PmuQAAAAJ:EkHepimYqZsC",
            "citation_id": "t77PmuQAAAAJ:EkHepimYqZsC",
            "authors": "P Harel, OI Shahar, O Ben-Shahar",
            "publication": "International Journal of Computer Vision 132 (9), 3428-3462, 2024",
            "cited_by": {
                "value": 3,
                "link": "https://scholar.google.com/scholar?oi=bibs&hl=en&cites=4021788807958281406",
                "serpapi_link": "https://serpapi.com/search.json?cites=4021788807958281406&engine=google_scholar&hl=en",
                "cites_id": "4021788807958281406"
            },
            "year": "2024",
            "path": "tests/data/Ohad Ben-shahar/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"
    }

    supervisor_metadata = {
        "supervisor_name":"Ohad Ben-Shahar",
        "available_pdfs": [paper_metadata],
        "author": {
            "name": "Ohad Ben-Shahar",
            "affiliations": "Ben Gurion University of the Negev, Israel",
            "email": "Verified email at cs.bgu.ac.il",
            "website": "http://www.cs.bgu.ac.il/~ben-shahar",
            "interests": [
                {
                    "title": "Computational Vision",
                    "link": "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:computational_vision",
                    "serpapi_link": "https://serpapi.com/search.json?engine=google_scholar_profiles&hl=en&mauthors=label%3Acomputational_vision"
                },
                {
                    "title": "Computer Vision",
                    "link": "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:computer_vision",
                    "serpapi_link": "https://serpapi.com/search.json?engine=google_scholar_profiles&hl=en&mauthors=label%3Acomputer_vision"
                },
                {
                    "title": "Human Visual Perception",
                    "link": "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:human_visual_perception",
                    "serpapi_link": "https://serpapi.com/search.json?engine=google_scholar_profiles&hl=en&mauthors=label%3Ahuman_visual_perception"
                },
                {
                    "title": "Visual Neuroscience",
                    "link": "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=label:visual_neuroscience",
                    "serpapi_link": "https://serpapi.com/search.json?engine=google_scholar_profiles&hl=en&mauthors=label%3Avisual_neuroscience"
                }
            ],
            "thumbnail": "https://scholar.googleusercontent.com/citations?view_op=view_photo&user=t77PmuQAAAAJ&citpid=8"
        },
    }

    def test_index_paper_1(self):
        settings = {
            "vector_store":{
                "type":"InMemoryVectorStore"
            }
        }

        pipeline = indexing_pipeline.IndexingPipeline(override_settings=settings)

        path = "tests/data/Ohad Ben-shahar/Harel_et_al-2024-International_Journal_of_Computer_Vision.pdf"
        pipeline.index_paper_(path,self.supervisor_metadata["supervisor_name"],self.paper_metadata)

        docs = pipeline.vector_store.store.items()
        self.assertEqual(len(docs),1)

        top_n = 10
        for index, (id, doc) in enumerate(pipeline.vector_store.store.items()):
            if index < top_n:
                # docs have keys 'id', 'vector', 'text', 'metadata'
                print(f"{id}: {doc['text']}")
            else:
                break

    def test_index_supervisor_brief(self):
        settings = {
            "vector_store":{
                "type":"InMemoryVectorStore"
            }
        }

        pipeline = indexing_pipeline.IndexingPipeline(override_settings=settings)
        pipeline.index_supervisor_brief_(self.supervisor_metadata)

        docs = pipeline.vector_store.store.items()
        self.assertEqual(len(docs),1)

        top_n = 10
        for index, (id, doc) in enumerate(pipeline.vector_store.store.items()):
            if index < top_n:
                # docs have keys 'id', 'vector', 'text', 'metadata'
                print(f"{id}: {doc['text']}")
            else:
                break


    def test_index_supervisor(self):
        settings = {
            "vector_store":{
                "type":"InMemoryVectorStore"
            }
        }

        pipeline = indexing_pipeline.IndexingPipeline(override_settings=settings)
        pipeline.index_supervisor(self.supervisor_metadata)

        docs = pipeline.vector_store.store.items()
        num_brief_docs = 1
        num_paper_docs = 1
        self.assertEqual(len(docs),num_brief_docs+num_paper_docs)

        top_n = 10
        for index, (id, doc) in enumerate(pipeline.vector_store.store.items()):
            if index < top_n:
                # docs have keys 'id', 'vector', 'text', 'metadata'
                print(f"{id}: {doc['text']}")
            else:
                break

    def test_run(self):
        settings = {
            "vector_store":{
                "type":"InMemoryVectorStore"
            }
        }

        metadata_retriever = indexing_pipeline.PapersMetadataRetriever(tests_root_folder)
        pipeline = indexing_pipeline.IndexingPipeline(override_settings=settings,metadata_retriever=metadata_retriever)
        pipeline.run()

        num_brief_docs = metadata_retriever.get_num_total_supervisors()
        num_paper_docs = metadata_retriever.get_num_total_papers()
        docs = pipeline.vector_store.store.items()
        self.assertEqual(len(docs),num_brief_docs+num_paper_docs)

        top_n = 3
        for index, (id, doc) in enumerate(pipeline.vector_store.store.items()):
            if index < top_n:
                # docs have keys 'id', 'vector', 'text', 'metadata'
                print(f"{id}: {doc['text']}")
            else:
                break
    
    def test_run_faiss_save_db(self):
        save_folder = "tests/tmp/faiss_vector_db"
        settings = {
            "vector_store":{
                "type":"FAISS",
                "save_folder": save_folder
            }
        }
        
        metadata_retriever = indexing_pipeline.PapersMetadataRetriever(tests_root_folder)
        pipeline = indexing_pipeline.IndexingPipeline(override_settings=settings,metadata_retriever=metadata_retriever)
        pipeline.run()

        num_brief_docs = metadata_retriever.get_num_total_supervisors()
        num_paper_docs = metadata_retriever.get_num_total_papers()
        docs = pipeline.vector_store.store.items()
        self.assertEqual(len(docs),num_brief_docs+num_paper_docs)

        if os.path.exists(save_folder):
            shutil.rmtree(save_folder)
        else:
            self.assertFalse(True,f"vector DB was not created in {save_folder}")


class TestPromptsTemplates(unittest.TestCase):
    def test_get_supervisor_brief_1(self):
        name = "Ohad Ben-Shahar"
        affiliations = "Ben Gurion University of the Negev, Israel"
        interests = ["Computational Vision","Computer Vision","Human Visual Perception","Visual Neuroscience"]
        
        brief = indexing_pipeline.get_supervisor_brief(name,affiliations,interests)

        # TODO: check for whitespace etc
        print(brief)
    
    def test_get_supervisor_brief_2(self):
        name = "Ohad Ben-Shahar"
        affiliations = "Ben Gurion University of the Negev, Israel"
        interests = ["Computational Vision"]
        
        brief = indexing_pipeline.get_supervisor_brief(name,affiliations,interests)

        # TODO: check for whitespace etc
        print(brief)
        self.assertNotIn(", and",brief)
    
    def test_get_supervisor_brief_3(self):
        name = "Ohad Ben-Shahar"
        affiliations = "Ben Gurion University of the Negev, Israel"
        interests = []
        
        brief = indexing_pipeline.get_supervisor_brief(name,affiliations,interests)

        # TODO: check for whitespace etc
        self.assertNotIn("research",brief)
        print(brief)


    def test_get_overview_1(self):
        supervisor_name = "Ohad Ben-Shahar"
        title = "Pictorial and apictorial polygonal jigsaw puzzles from arbitrary number of crossing cuts"
        authors = "P Harel, OI Shahar, O Ben-Shahar"
        publication = "International Journal of Computer Vision 132 (9), 3428-3462, 2024"
        year = "2024"
        num_cites = 3
        
        text = indexing_pipeline.get_paper_overview(supervisor_name,title,publication,year,authors,num_cites)

        print(text)

class TestExtractingAbstract(unittest.TestCase):

    def load_paper_tester(self,root_folder):
        metadata_retriever = indexing_pipeline.PapersMetadataRetriever(root_folder)
        print()
        abstract_errors = []
        read_errors = []

        for supervisor_metadata in metadata_retriever.get_supervisors_metadata():
            print(f"supervisor: {supervisor_metadata["supervisor_name"]}.")
            for paper in supervisor_metadata["available_pdfs"]:
                print(f"\t{paper["path"]}")
                try:
                    text = pdf_handler.read_pdf(paper["path"])
                except Exception as e:
                    read_errors.append({
                        "path":paper["path"],
                        "error":e
                    })
                    continue
                try:
                    abstract_text = pdf_handler.extract_absract(text)
                except Exception as e:
                    abstract_errors.append({
                        "path":paper["path"],
                        "error":e
                    })

        '''Raise intentionally the error'''
        num_failed = len(abstract_errors)+len(read_errors)
        print(f"Number of failed paper to extract their abstract is {num_failed}:")
        
        print(f"********** abstract_errors ({len(abstract_errors)})**********")
        print(abstract_errors)
        
        print(f"********** read_errors ({len(read_errors)})**********")
        print(read_errors)

        for paper in abstract_errors:
            try:
                print(paper)
                text = pdf_handler.read_pdf(paper["path"])
                abstract_text = pdf_handler.extract_absract(text)
            except Exception as e:
                # re run the error to put conviently breakpoint
                text = pdf_handler.read_pdf(paper["path"])
                abstract_text = pdf_handler.extract_absract(text)

    def test_no_exception_tests_data(self):
        self.load_paper_tester(tests_root_folder)
    
    def test_no_exception_prod_data(self):
        self.load_paper_tester(PAPERS_FOLDER)



if __name__ == "__main__":
    unittest.main()