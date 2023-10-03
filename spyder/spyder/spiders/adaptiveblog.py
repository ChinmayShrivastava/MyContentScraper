from .scraper import *
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class AdaptiveBlogSpider(scrapy.Spider):
    name = "adaptiveblog"
    allowed_domains = ["adaptive.live/blog"]
    start_urls = ["https://adaptive.live/blog"]

    link_extractor = LinkExtractor(unique=True)

    def parse(self, response):
        for link in self.link_extractor.extract_links(response):
            if 'blog/category' in link.url:
                yield scrapy.Request(link.url, callback=self.parse)
            elif link.url.endswith('blog'):
                pass
            elif 'blog' in link.url:
                # extract title from response meta
                title = response.meta.get('title')
                # find the author and date from the div with class 'text-left mt-2 sm:mt-12'
                # author_date = response.css('div.text-left.mt-2.sm\:mt-12 ::text').getall()
                data = {
                    'url': link.url,
                    'title': title,
                    # 'date': author_date,
                }
                with open('adaptiveblog.csv', 'a') as f:
                    f.write(f"{data['url']}, {data['title']} \n")
                yield scrapy.Request(link.url, callback=self.parse)
        