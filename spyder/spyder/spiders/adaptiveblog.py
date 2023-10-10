from .scraper_old import *
from .keyword_extractor import get_keyword
from .script import *
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import psycopg2
import json

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

# create a table 'urls' with columns
# url (primary key)
# domain (text, secondary key)
cur.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        url TEXT PRIMARY KEY,
        domain TEXT,
        author TEXT,
        pubdate TEXT
    )
""")
conn.commit()

# create a table 'topics' with columns
# topic (text, primary key)
cur.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        topic TEXT PRIMARY KEY
    )
""")
conn.commit()

# create a table 'resources' with columns
# url (foreign key to the url column in the urls table, secondary key)
# hid (text)
# heading (text)
# hnum (integer)
# next heading (integer or null)
# subheading (integer or null)
# content (text)
cur.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        url TEXT REFERENCES urls(url),
        hid TEXT,
        heading TEXT,
        hnum INTEGER,
        next_heading INTEGER,
        subheading INTEGER,
        content TEXT,
        topics TEXT
    )
""")
conn.commit()

class AdaptiveBlogSpider(scrapy.Spider):
    name = "adaptiveblog"
    allowed_domains = ["adaptive.live/blog"]
    start_urls = ["https://adaptive.live/blog"]

    link_extractor = LinkExtractor(unique=True)

    def parse(self, response):

        # # assume `response` is a scrapy.http.response.html.HtmlResponse object
        # text = response.text
        # url = response.url
        # headers = response.headers
        # status = response.status

        # # create a requests.models.Response object from the text and other attributes
        # new_response = requests.models.Response()
        # new_response._content = text.encode("utf-8")
        # new_response.url = url
        # new_response.headers = headers
        # new_response.status_code = status

        for link in self.link_extractor.extract_links(response):

            # if url exists in urls table, skip
            cur.execute("""
                SELECT url FROM urls WHERE url = %s
            """, (link.url,))
            if cur.fetchone():
                continue

            if 'blog/category' in link.url:
                yield scrapy.Request(link.url, callback=self.parse)
            elif link.url.endswith('blog'):
                pass
            elif 'blog' in link.url:

                res, soup = scrape_url(link.url)

                author, date_pub = get_adaptive_author_date(link.url)

                # insert url into urls table
                data = {
                    'url': link.url,
                    'domain': link.url.split('/')[2],
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
                # # extract title from response meta
                # article, title, lang, soup = contentfinder(link.url)
                # print(article)
                # data = {
                #     'url': link.url,
                #     'title': title,
                #     'lang': lang,
                #     'article': article.text,
                # }
                # # insert data into database
                # cur.execute("""
                #     INSERT INTO adaptiveblog (url, title, lang, article)
                #     VALUES (%(url)s, %(title)s, %(lang)s, %(article)s)
                # """, data)
                # conn.commit()
                # # with open('adaptiveblog.csv', 'a') as f:
                # #     f.write(f"{data['url']}, {data['title']} \n")
                yield scrapy.Request(link.url, callback=self.parse)
        