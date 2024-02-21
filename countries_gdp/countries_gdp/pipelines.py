# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import sqlite3


class CountriesGdpPipeline:
    def process_item(self, item, spider):
        if not isinstance(item["gdp"], float):
            raise DropItem("Missing GDP value. Item excluded.")
        return item


class SaveToDatabasePipeline:
    def __init__(self):
        self.conn = sqlite3.connect("countries_gdp.db")
        self.cur = self.conn.cursor()

    def open_spider(self, spider):
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS countries_gdp (country_name TEXT PRIMARY KEY, region TEXT, 
        gdp REAL, year INTEGER)"""
        )
        self.conn.commit()

    def process_item(self, item, spider):
        self.cur.execute(
            """INSERT INTO countries_gdp(country_name, region, 
        gdp, year) VALUES (?,?,?,?)""",
            (item["country_name"], item["region"], item["gdp"], item["year"]),
        )
        self.conn.commit()

    def close_spider(self):
        self.conn.close()


class NoDuplicateCountryPipeline:
    def __init__(self) -> None:
        self.countries_seen = set()

    def process_item(self, item, spider):
        country_name = item["country_name"]
        if country_name in self.countries_seen:
            raise DropItem(f"duplicate country found {item}")
        else:
            self.countries_seen.add(country_name)
            return item
