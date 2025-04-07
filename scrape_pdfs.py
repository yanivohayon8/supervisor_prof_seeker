import os
import json
from scraper.utils import run_spider
from scraper.scraper.spiders.googlescholar_spider import GoogleScholarArticlesSpider
from glob import glob
import time


from multiprocessing import Process

def get_author_details(supervisor_folder:str):
    path = os.path.join(supervisor_folder,"author_details.json")

    try:
        with open(path,"r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_articles(author_details:dict):
    return author_details["articles"]

def get_google_scholar_url(article:dict):
    return article["link"]

def get_title(article:dict):
    return article["title"]

def scrape_papers(supervisor_folder:str):
    try:
        print(f"********************************* Next is {supervisor_folder} *********************************")
        author_details = get_author_details(supervisor_folder)

        if not author_details:
            print(f"author details in {supervisor_folder} are not present...")
            return
        
        time.sleep(3)

        articles = get_articles(author_details)
        print(f"\t Found {len(articles)} articles")

        urls = []
        titles = []
        for i,article in enumerate(articles):
            urls.append(get_google_scholar_url(article))
            titles.append(str(i)+"_"+get_title(article))

        save_folder = os.path.join(supervisor_folder,"papers")

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        settings = {
            "ITEM_PIPELINES":{
                "scraper.scraper.pipelines.GoogleScholarAuditPipeline":300,
            }
        }

        run_spider(GoogleScholarArticlesSpider,settings=settings,
                starting_urls=urls,save_folder=save_folder,articles_titles=titles)
    except Exception as e:
        print(f"A problem with {supervisor_folder}, {e}")

if __name__ == "__main__":
    supervisor_folders = [folder for folder in glob("data/google_scholar/*")]
    # scrape_papers(supervisor_folders[0])
    # scrape_papers(supervisor_folders[1])
    # scrape_papers(supervisor_folders[2]) # many blocks (retry?)
    # scrape_papers(supervisor_folders[3]) 
    # scrape_papers(supervisor_folders[4]) 
    # scrape_papers(supervisor_folders[5]) 
    # scrape_papers(supervisor_folders[6]) 
    # scrape_papers(supervisor_folders[7]) 
    # scrape_papers(supervisor_folders[8]) 
    # scrape_papers(supervisor_folders[9]) 
    # scrape_papers(supervisor_folders[10]) 
    # scrape_papers(supervisor_folders[11]) 
    # scrape_papers(supervisor_folders[12]) 
    # scrape_papers(supervisor_folders[13]) 
    # scrape_papers(supervisor_folders[14]) 
    # scrape_papers(supervisor_folders[15]) 
    # scrape_papers(supervisor_folders[16]) 
    # scrape_papers(supervisor_folders[17]) 
    # scrape_papers(supervisor_folders[18]) 
    # scrape_papers(supervisor_folders[19]) 
    # scrape_papers(supervisor_folders[20]) 
    # scrape_papers(supervisor_folders[21])

    # proces = Process(target=scrape_papers,args=[supervisor_folders[22]])
    # proces.start()
    # proces.join()
    
    # for i in range(23,25):
    #     print(f"Starting process of {i}")
    #     proces = Process(target=scrape_papers,args=[supervisor_folders[i]])
    #     proces.start()
    #     proces.join()
    
    # for i in range(25,28):
    #     print(f"********************************* Starting process of {i} *********************************")
    #     proces = Process(target=scrape_papers,args=[supervisor_folders[i]])
    #     proces.start()
    #     proces.join()
    
    # for i in range(28,35):
    #     print(f"********************************* Starting process of {i} *********************************")
    #     proces = Process(target=scrape_papers,args=[supervisor_folders[i]])
    #     proces.start()
    #     proces.join()
    
    # for i in range(35,40):
    #     print(f"********************************* Starting process of {i} *********************************")
    #     proces = Process(target=scrape_papers,args=[supervisor_folders[i]])
    #     proces.start()
    #     proces.join()

    # for i in range(40,43):
    #     print(f"********************************* Starting process of {i} *********************************")
    #     proces = Process(target=scrape_papers,args=[supervisor_folders[i]])
    #     proces.start()
    #     proces.join()
    #     time.sleep(5)

    for i in range(43,len(supervisor_folders)):
        print(f"********************************* Starting process of {i} *********************************")
        proces = Process(target=scrape_papers,args=[supervisor_folders[i]])
        proces.start()
        proces.join()
        time.sleep(5)

        

    