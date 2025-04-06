import scrapy
import os

class GoogleScholarArticlesSpider(scrapy.Spider):
    name = "google_scholar_article"

    def __init__(self, starting_urls:list,save_folder:str,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for url in starting_urls:
            assert url.startswith("https://scholar.google.com"), f"{url} is not a google scholar link"
        
        self.inputted_starting_urls = starting_urls
        self.save_folder = save_folder
    
    def start_requests(self):
        for url in self.inputted_starting_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self,response):
        pdf_url = response.css("div.gsc_oci_title_ggi a").attrib["href"]
        yield scrapy.Request(url=pdf_url, callback=self.save_pdf)

    def save_pdf(self,response):
        name = response.url.split('/')[-1]
                
        if not name.endswith(".pdf"):
            name = name + ".pdf"

        with open(os.path.join(self.save_folder,name), 'wb') as f:
            f.write(response.body)