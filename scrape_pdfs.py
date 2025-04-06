import os
import json
from scraper.utils import run_spider
from scraper.scraper.spiders.googlescholar_spider import GoogleScholarArticlesSpider


def get_author_details(supervisor_folder:str):
    path = os.path.join(supervisor_folder,"author_details.json")

    with open(path,"r") as f:
        return json.load(f)

def get_articles(author_details:dict):
    return author_details["articles"]

def get_google_scholar_url(article:dict):
    return article["link"]

def get_title(article:dict):
    return article["title"]

if __name__ == "__main__":
    supervisor_folder = "data/google_scholar/25_Liron Cohen"
    author_details = get_author_details(supervisor_folder)
    articles = get_articles(author_details)

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

    