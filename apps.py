from scrapy.crawler import
from qna_crawler.spiders import ETOOSSpider, MegaSpider, SkySpider

if __name__ =='__main__':
    process = CrawlerProcess(get_project_settings())

    process.crawl(ETOOSSpider)
    process.crawl(MegaSpider)