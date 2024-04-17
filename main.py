import os
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

scraper = cloudscraper.create_scraper()

url_shop = 'https://www.redbubble.com'

is_enable_mongo = os.getenv('ENABLE_MONGO', 'False') == 'True'
client = MongoClient(os.getenv('ATLAS_URI'))
db = client[os.getenv('DB_NAME')]
collection = db[os.getenv('COLLECTION_NAME')]

# unique keyword and iaCode
collection.create_index([('keyword', 1), ('iaCode', 1)], unique=True)


def download_url(url: str) -> str:
    print(url)
    response = scraper.get(url)
    return response.text


class Crawler:
    def __init__(self, urls=None):
        if urls is None:
            urls = []

        self.failed_urls = set()
        self.visited_urls = set()
        self.urls_to_visit = urls
        self.keywords = set()

    def get_keyword(self, content: str, url: str):
        soup = BeautifulSoup(content, 'html.parser')

        # get all links from div.styles__resultsProductsContainer--1Xv9D > div.styles__carouselInner--3mwKu
        links = [a['href'] for a in
                 soup.select('div.styles__resultsProductsContainer--1Xv9D div.styles__carouselInner--3mwKu a')]

        # skip if link is already visited
        links = [link for link in links if link not in self.visited_urls]
        self.urls_to_visit.extend(links)

        # first remove the /shop/ from the links
        keyword_and_category = [link.replace('/shop/', '') for link in links]

        # remove keywords that are already in the set
        keyword_and_category = [keyword for keyword in keyword_and_category if keyword not in self.keywords]
        self.keywords.update(keyword_and_category)

        # insert into mongo if enabled
        if is_enable_mongo:
            for keyword in keyword_and_category:
                data = keyword.split('+')

                iaCode = data.pop()
                data = '+'.join(data).replace('+', ' ')

                try:  # insert into mongo
                    collection.insert_one({'keyword': data, 'iaCode': iaCode})
                except Exception as e:
                    print(e)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)

            url_crawl = url_shop + url
            try:
                content = download_url(url_crawl)
                self.get_keyword(content, url)
                self.visited_urls.add(url_crawl)

            except Exception as e:
                print(e)
                self.failed_urls.add(url_crawl)

        print('Failed URLs:', self.failed_urls)


if __name__ == '__main__':
    Crawler(urls=['/shop/funny+clothing']).run()
