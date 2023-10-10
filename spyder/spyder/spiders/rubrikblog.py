import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
import json
from .scraper import *
from .script import *
from .keyword_extractor import get_keyword

# connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5450,
    database="postgres",
    user="postgres",
    password="postgres"
)

# create cursor
cur = conn.cursor()

class RubrikblogSpider(scrapy.Spider):
    name = "rubrikblog"
    allowed_domains = ["rubrik.com/blog"]
    number = 0
    link_extractor = LinkExtractor(unique=True)
    start_urls = ["https://rubrik.com/blog/"]
    first = False

    def parse(self, response):

        if not self.first:
            self.first = True
            # load json file
            with open('rubrik.json') as f:
                links = json.load(f)

        # iterate through links
        for link in links:

            # if url exists in urls table, skip
            cur.execute("""
                SELECT url FROM urls WHERE url = %s
            """, (link,))
            if cur.fetchone():
                continue

            if link.endswith('blog/'):
                continue

            # if url is not a blog post, skip
            if 'blog/' in link:

                res, soup = scrape_url(link)

                author, date_pub = get_rubrik_author_date(link)

                # insert url into urls table
                data = {
                    'url': link,
                    'domain': link.split('/')[2],
                    'author': author,
                    # date is string of format 'mmddyyyy'
                    'pubdate': date_pub
                }

                cur.execute("""
                    INSERT INTO urls (url, domain, author, pubdate)
                    VALUES (%(url)s, %(domain)s, %(author)s, %(pubdate)s)
                    ON CONFLICT DO NOTHING
                """, data)
                conn.commit()

                i=0
                for element in res:

                    topics = get_keyword('heading:' + element[2] + '\n' + 'content:' + element[5])
                    for topic in topics:
                        # if topic not in topics table, insert topic into topics table
                        cur.execute("""
                            INSERT INTO topics (topic)
                            VALUES (%s)
                            ON CONFLICT DO NOTHING
                        """, (topic,))
                        conn.commit()

                    data = {
                        'url': element[0],
                        'hid': element[1],
                        'heading': element[2],
                        'hnum': i,
                        'next_heading': element[3],
                        'subheading': element[4],
                        'content': element[5],
                        'topics': json.dumps(topics)
                    }

                    cur.execute("""
                        INSERT INTO resources (url, hid, heading, hnum, next_heading, subheading, content, topics)
                        VALUES (%(url)s, %(hid)s, %(heading)s, %(hnum)s, %(next_heading)s, %(subheading)s, %(content)s, %(topics)s)
                    """, data)

                    conn.commit()
                    i+=1

                yield scrapy.Request(link, callback=self.parse)
