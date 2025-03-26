# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import json

class ScraperPipeline:
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline:
    def __init__(self):
        self.names_seen = set()

    def process_item(self,item,spider):
        adapter = ItemAdapter(item)
        name = adapter["name"]

        if name in self.names_seen:
            raise DropItem(f"Item name already seen: {name}")
        else:
            self.names_seen.add(name)
            return item
        

class JsonWriterPipeline:
    def open_spider(self,spider):
        self.file = open("supervisors.jsonl","w")
    
    def close_spider(self,spider):
        self.file.close()
    
    def process_item(self,item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) +"\n"
        self.file.write(line)

        return item