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

    for i in range(len(supervisor_folders)):
        print(f"********************************* Starting process of {i} *********************************")
        proces = Process(target=scrape_papers,args=[supervisor_folders[i]])
        proces.start()
        proces.join()
        time.sleep(5)

        

    