from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup
from datetime import datetime
import time, json, random

class Subreddit_Scraper():
    def __init__(self, link):
        # assumed in the same path, has to be compatiable with the chrome version
        service = Service(executable_path="C:/Users/Febru/Desktop/de_project/Reddit-Posts-Analysis\chromedriver.exe")
        self.driver = webdriver.Chrome(service=service)
        self.link = link
        self.post_ids = set()
        self.post_details = []

    def scroll(self, max_scroll=10):
        curr_height = self.driver.execute_script("return document.body.scrollHeight")
        html_source = None
        n = 0

        while True:
            self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(random.randint(3,6))

            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == curr_height or n == max_scroll:
                # print("Reached the end!/reached max scroll")
                html_source = self.driver.page_source
                break

            curr_height = new_height
            n += 1
        return html_source

    def get_post_links(self, max_scroll=1, n_scroll=1):
        """
        Args:
            max_scroll: max num of scrolling down every time we call scroll()
            n_scroll: num of times to call scroll()
        """
        self.driver.get(self.link)
        self.driver.maximize_window()

        time.sleep(6)
        for i in range(n_scroll):
            html_source = self.scroll(max_scroll)
            parser = BeautifulSoup(html_source, 'html.parser')
            post_links = parser.find_all('a', {'slot': 'full-post-link'})
            cnt = 0
            for link in post_links:
                self.post_ids.add(link['href'].split('/')[4])
                cnt += 1
            print(f'Successfully parsed {cnt} post_ids')

    def get_post_html(self, post_id):
        base_url='https://www.reddit.com/'
        format='.json'
        full_link=base_url+post_id+format
        self.driver.get(full_link)
        return self.driver.page_source
    
    def get_post_details(self, post_html):
        attrs = ['id', 'author', 'title', 'discussion_type', 'num_comments', 'ups', 'upvote_ratio', 'created_utc', 'is_video', 'selftext']
        parser=BeautifulSoup(post_html, 'html.parser')
        try:
            post = json.loads(parser.find('body').get_text())
            post_details = post[0]['data']['children'][0]['data']
            post_details_dict = {attr: post_details.get(attr) for attr in attrs}
            self.post_details.append(post_details_dict)
            print(f'Added post {post_details_dict['id']}')

        except json.decoder.JSONDecodeError:
            print('unable to parse it, invalid json format')

    def get_all_posts(self):
        if not self.post_ids:
            print('Post_ids is empty, please run get_post_links() first!')
            return
        for post_id in self.post_ids:
            time.sleep(random.randint(2, 8))
            post_html = self.get_post_html(post_id=post_id)
            self.get_post_details(post_html=post_html)
        
        print('All done!')

    def save(self):
        if not self.post_details:
            print('post_details is empty, please run get_all_posts() first')
            return
        curr_date=datetime.now().strftime("%Y-%m-%d")
        filename = f"subreddit_{curr_date}.json"
        with open(filename, 'w') as f:
            json.dump(self.post_details, f)
        print(f"Saved to {filename}")

    def destroy(self):
        self.driver.stop()


if __name__ == "__main__":
    start_time = time.time()
    link='https://www.reddit.com/r/TikTok/top/?t=month'
    scraper_obj = Subreddit_Scraper(link)
    scraper_obj.get_post_links(max_scroll=1, n_scroll=30)
    scraper_obj.get_all_posts()
    scraper_obj.save()
    end_time = time.time()
    print(f'Time Taken: {end_time - start_time}')