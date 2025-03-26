import scrapy
from scrapy.loader import ItemLoader
from scraper.scraper.items import SupervisorItem

from pathlib import Path


class BguCsSpider(scrapy.Spider):
    name="bgu_cs"
    start_urls = [
        "https://csdynamicweb.cs.bgu.ac.il/ResearchAreas.aspx?area=9",
        "https://csdynamicweb.cs.bgu.ac.il/ResearchAreas.aspx?area=8", # Interdisciplinary Research
        "https://csdynamicweb.cs.bgu.ac.il/ResearchAreas.aspx?area=5", # Vision, Graphics, and Geometry
        "https://csdynamicweb.cs.bgu.ac.il/ResearchAreas.aspx?area=4",#Computer Systems, Communication and Software Engineering
        "https://csdynamicweb.cs.bgu.ac.il/ResearchAreas.aspx?area=1",#AI, Machine Learning and Data Science
        "https://csdynamicweb.cs.bgu.ac.il/ResearchAreas.aspx?area=2",#Theory of Computer Science
    ]

    def parse(self,response):
        for link in response.xpath("//ul/li/a"):
            loader = ItemLoader(item=SupervisorItem(), selector=link)
            loader.add_xpath("name", "./@title")
            loader.add_xpath("name", "./text()")
            loader.add_xpath("personal_website_url", "./@href")
            yield loader.load_item()
        
