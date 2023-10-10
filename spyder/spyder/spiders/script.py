from bs4 import BeautifulSoup
import re
import json
import scrapy
import datetime
import requests

def get_adaptive_author_date(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # new soup is section with class 'text-left mt-2 sm:mt-12'
    new_soup = soup.find("div", class_="text-left mt-2 sm:mt-12")
    # find the author name and publication date, third element inside new_soup
    author_date = new_soup.find_all('div')[2].text
    author, date_str = re.split(r"\s*[⋅•]\s*", author_date)
    date = datetime.datetime.strptime(date_str, "%b %d, %Y").strftime("%m%d%Y")
    return author.lower(), date.lower()

def get_strongdm_author_date(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # author is the text in an <a> tag with rel="author"
    try:
        author = soup.find("a", rel="author").text
    except:
        author = ''
    # date is inside div wito class "date". Ignore the span inside this div
    # it looks like this: <div class="date"><span>SOME TEXT </span>May 20, 2020</div>
    try:
        date_str = soup.find("div", class_="date").text.split(':')[1].strip()
        date = datetime.datetime.strptime(date_str, "%B %d, %Y").strftime("%m%d%Y")
    except:
        date_str = ''
        date = ''
    return author.lower(), date.lower()

def get_bigid_author_date(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # author is the text in an <a> tag with class='post-author-name'
    try:
        author = soup.find("a", class_="post-author-name").text
    except:
        author = ''
    # date is inside time tag with class 'updated'
    try:
        date_str = soup.find("time", class_="updated").text.strip() # format mm.dd.yyyy
        # convert to mmddyyyy
        date = date_str.split('.')[0] + date_str.split('.')[1] + date_str.split('.')[2]
    except:
        date_str = ''
        date = ''
    return author.lower(), date.lower()

def get_rubrik_author_date(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # export the html to a file to see the structure
    with open('rubrik.html', 'w') as f:
        f.write(soup.prettify())
    # author is the alt text in the img under div with class "author-byline wrapper row" <img alt="Benjamin Troch" class="lazy image--center" data-src="/content/dam/rubrik/blog/author-bio/benjamin-troch.png"/>
    # find it by matching the href pattern
    try:
        imgdiv = soup.find("div", class_="author-byline wrapper row")
        author = imgdiv.find("img", alt=re.compile('.*')).get('alt')
    except Exception as e:
        print(e)
        author = ''
    # date is inside p tag with class 'eyebrow', there are two, we want the first one
    try:
        date_str = soup.find_all("p", class_="eyebrow")[0].text.split('|')[0].strip() # format Mon dd, yyyy
        # convert to mmddyyyy
        date = datetime.datetime.strptime(date_str, "%b %d, %Y").strftime("%m%d%Y")
    except:
        date_str = ''
        date = ''
    return author.lower(), date.lower()

# if __name__ == '__main__':

#     url = 'https://www.rubrik.com/blog/company/23/7/introducing-the-rsc-rubrik-servicenow-integration'
#     html = requests.get(url).text
#     soup = BeautifulSoup(html, 'lxml')

#     print(get_rubrik_author_date(url))