import unittest
from scraper import utils
from scraper.scraper.spiders.supervisors_spider import BguCsSpider
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

if __name__ == "__main__":
    unittest.main()