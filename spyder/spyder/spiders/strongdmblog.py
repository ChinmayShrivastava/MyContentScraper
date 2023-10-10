import scrapy
from scrapy.linkextractors import LinkExtractor
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

class StrongdmblogSpider(scrapy.Spider):
    name = "strongdmblog"
    allowed_domains = ["www.strongdm.com/blog"]
    start_urls = ["https://www.strongdm.com/blog",
                  'https://www.strongdm.com/blog/page/2',
                  'https://www.strongdm.com/blog/page/3',
                  'https://www.strongdm.com/blog/page/4',
                  'https://www.strongdm.com/blog/page/5',
                  'https://www.strongdm.com/blog/page/6',
                  'https://www.strongdm.com/blog/page/7',
                  'https://www.strongdm.com/blog/page/8',
                  'https://www.strongdm.com/blog/page/9',
                  'https://www.strongdm.com/blog/page/10',
                  'https://www.strongdm.com/blog/page/11',
                  'https://www.strongdm.com/blog/page/12',
                  'https://www.strongdm.com/blog/page/13',
                  'https://www.strongdm.com/blog/page/14',
                  'https://www.strongdm.com/blog/page/15',
                  'https://www.strongdm.com/blog/page/16',
                  'https://www.strongdm.com/blog/page/17',
                  'https://www.strongdm.com/blog/page/18',
                  'https://www.strongdm.com/blog/page/19',
                  'https://www.strongdm.com/blog/page/20',
                  'https://www.strongdm.com/blog/page/21',
                  'https://www.strongdm.com/blog/page/22',
                  'https://www.strongdm.com/blog/page/23']

    link_extractor = LinkExtractor(unique=True)

    def parse(self, response):

        for link in self.link_extractor.extract_links(response):

            # if url exists in urls table, skip
            cur.execute("""
                SELECT url FROM urls WHERE url = %s
            """, (link.url,))
            if cur.fetchone():
                continue

            if 'blog/tag' in link.url:
                yield scrapy.Request(link.url, callback=self.parse)
            elif 'blog/page' in link.url:
                yield scrapy.Request(link.url, callback=self.parse)
            elif link.url.endswith('blog'):
                pass
            elif link.url.endswith('blog/'):
                pass
            elif 'blog' in link.url:

                res, soup = scrape_url(link.url)

                author, date_pub = get_strongdm_author_date(link.url)

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