from scrapy.crawler import CrawlerProcess
# from scraper.scraper.spiders.supervisor_spider import SupervisorSpider
from scrapy.utils.project import get_project_settings

def create_crawler_process_(settings:dict=None):
    custom_settings = get_project_settings()

    if settings:
        custom_settings.update(settings)

    process = CrawlerProcess(custom_settings)

    return process

def start_crawl_(spider_class, process:CrawlerProcess):
    process.crawl(spider_class)
    process.start()

def run_spider(spider_class,settings:dict=None):
    process = create_crawler_process_(settings)
    start_crawl_(spider_class,process)
    






