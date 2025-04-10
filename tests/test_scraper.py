import unittest

import scrapy.spiders
from scraper import utils
from scraper.scraper.spiders.supervisors_spider import BguCsSpider
from scraper.scraper.spiders.googlescholar_spider import GoogleScholarArticlesSpider
import scrapy
import json
import os

class TestUtils(unittest.TestCase):

    def test_runner_QuotesSpider(self):
        # A dummy scraper from the tutorial https://docs.scrapy.org/en/latest/intro/tutorial.html
        class QuotesSpider(scrapy.Spider):
            name = "quotes"
            start_urls = [
                "https://quotes.toscrape.com/page/1/",
            ]

            def parse(self, response):
                for quote in response.css("div.quote"):
                    yield {
                        "text": quote.css("span.text::text").get(),
                        "author": quote.css("span small::text").get(),
                        "tags": quote.css("div.tags a.tag::text").getall(),
                    }

                yield from response.follow_all(css="ul.pager a",callback=self.parse)

        output_path = "tests/QuotesSpider_items.json"
        settings={
            "FEEDS": {
                output_path: {"format": "json"},
            },
        }

        utils.run_spider(QuotesSpider,settings=settings)

        try:
            with open(output_path) as f:
                data = json.load(f)

                self.assertGreater(len(data),0,"The spider did not scrape any items")
        except Exception:
            pass

        if os.path.exists(output_path):
            os.remove(output_path)


    def test_bgu_run_spider(self):
        output_path = "tests/test_bgu_run_spider.json"
        settings={
            "FEEDS": {
                output_path: {"format": "json"},
            },
        }

        utils.run_spider(BguCsSpider,settings=settings)

        try:
            with open(output_path) as f:
                data = json.load(f)
                self.assertGreater(len(data),0,"The spider did not scrape any items")
        except Exception:
            pass

        if os.path.exists(output_path):
            os.remove(output_path)


class TestPipelines(unittest.TestCase):
    def test_json_bgu(self):
        settings = {
            "ITEM_PIPELINES":{
                "scraper.scraper.pipelines.JsonWriterPipeline":300
            }
        }

        utils.run_spider(BguCsSpider,settings=settings)
    
    def test_duplicates_json_bgu(self):
        settings = {
            "ITEM_PIPELINES":{
                "scraper.scraper.pipelines.DuplicatesPipeline":300,
                "scraper.scraper.pipelines.JsonWriterPipeline":500
            }
        }

        utils.run_spider(BguCsSpider,settings=settings)


class TestGoogleScholarSpider(unittest.TestCase):
    def test_hardcoded_extract_link(self):
        class ScholarSpider(scrapy.Spider):
            name="Scholar"
            start_urls = ["https://scholar.google.com/citations?view_op=view_citation&hl=en&user=fxzlm6IAAAAJ&pagesize=100&citation_for_view=fxzlm6IAAAAJ:3s1wT3WcHBgC"] 

            def parse(self,response):
                link = response.css("div.gsc_oci_title_ggi a").attrib["href"]
                print()
                print(link)
                print()
                assert link == "https://arxiv.org/pdf/2502.19337"

        
        utils.run_spider(ScholarSpider)
    
    def test_hardcoded_download_pdf(self):
        class DownloaderSpider(scrapy.Spider):
            name="downloader"
            start_urls = ["https://arxiv.org/pdf/2502.19337"]

            def parse(self,response):
                name = response.url.split('/')[-1]
                
                if not name.endswith(".pdf"):
                    name = name + ".pdf"

                save_path = f"tests/tmp/{name}"

                with open(save_path, 'wb') as f:
                    f.write(response.body)
        
        utils.run_spider(DownloaderSpider)

    def test_GoogleScholarArticlesSpider_1(self):
        start_urls = [
            "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=fxzlm6IAAAAJ&pagesize=100&citation_for_view=fxzlm6IAAAAJ:3s1wT3WcHBgC"
            ] 
        
        save_folder = f"tests/tmp/"
        utils.run_spider(GoogleScholarArticlesSpider,starting_urls=start_urls,save_folder=save_folder)
        expecteed_file_path = os.path.join(save_folder,"2502.19337.pdf")

        self.assertTrue(os.path.exists(expecteed_file_path))
        os.remove(expecteed_file_path)


if __name__ == "__main__":
    unittest.main()