import cloudscraper
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper()

url_shop = 'https://www.redbubble.com'


def download_url(url):
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

    def get_keyword(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        links = [a['href'] for a in soup.select('div#TopicsCarousel a')]

        # skip if link is already visited
        links = [link for link in links if link not in self.visited_urls]
        self.urls_to_visit.extend(links)

        keywords = [span.text for span in soup.select('div#TopicsCarousel span')]
        self.keywords.update(keywords)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)

            url_crawl = url_shop + url
            try:
                content = download_url(url_crawl)
                self.get_keyword(content)
                print(self.keywords)
                self.visited_urls.add(url_crawl)

            except Exception as e:
                print(e)
                self.failed_urls.add(url_crawl)


if __name__ == '__main__':
    Crawler(urls=['/shop/?iaCode=u-tees&query=Anniversary&ref=search_box']).run()
