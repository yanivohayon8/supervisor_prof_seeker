import scrapy
import os
import re
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class GoogleScholarArticlesSpider(scrapy.Spider):
    name = "google_scholar_article"

    def __init__(self, starting_urls:list,save_folder:str,articles_titles:list[str]=None,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for url in starting_urls:
            assert url.startswith("https://scholar.google.com"), f"{url} is not a google scholar link"
        
        self.inputted_starting_urls = starting_urls
        self.save_folder = save_folder
        self.audits = []

        if not articles_titles:
            self.titles = [str(i)+".pdf" for i in range(len(self.inputted_starting_urls))]
        else:
            assert len(articles_titles) == len(starting_urls)
            self.titles = []

            for title in articles_titles:
                clean_title = re.sub('[|?*:<>\\\"/]',"",str(title))
                clean_title = clean_title+".pdf"
                self.titles.append(clean_title)
        
        self.url_to_title = {url:title for title,url in zip(self.titles,self.inputted_starting_urls)}
        self.pdf_url_to_google_url = {}
    
    def audit_success_(self,url):
        self.audits.append(
            {
                "status":"Success",
                "title":self.url_to_title.get(url,""),
                "error":"",
                "url":url,
            }
        )
    
    def audit_failure_(self,url,error):
        title = self.url_to_title.get(url)

        if not title:
            title = self.url_to_title.get(self.pdf_url_to_google_url.get(url),"")

        self.audits.append(
            {
                "status":"Failure",
                "title":title,
                "error":error,
                "url":url
            }
        )

    def start_requests(self):
        for url in self.inputted_starting_urls:
            yield scrapy.Request(url=url, callback=self.parse,errback=self.errback_httpbin)
        

    def parse(self,response):
        try:
            pdf_url = response.css("div.gsc_oci_title_ggi a").attrib["href"]
            self.pdf_url_to_google_url[pdf_url] = response.url
            yield scrapy.Request(url=pdf_url, callback=self.save_pdf,errback=self.errback_httpbin)
        except KeyError as e:
            self.audit_failure_(response.url,str(e))
        except Exception as e2:
            self.audit_failure_(response.url,str(e2))

    def save_pdf(self,response):
        try:
            google_url = self.pdf_url_to_google_url.get(response.url)
            title = self.url_to_title.get(google_url)

            if title:
                with open(os.path.join(self.save_folder,title), 'wb') as f:
                    f.write(response.body)
                
                self.audit_success_(google_url)
            else:
                self.audit_failure_(response.url,"Cannot get google url....")

        except Exception as e:
            self.audit_failure_(response.url,str(e))
    
    def errback_httpbin(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            self.audit_failure_(response.url,"HttpError")

        elif failure.check(DNSLookupError):
            request = failure.request
            self.audit_failure_(request.url,"DNSLookupError ")

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.audit_failure_(request.url,"TimeoutError ")
        else:
            self.audit_failure_(None,"In Errback")