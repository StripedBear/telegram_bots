from datetime import datetime
import requests
import asyncio
from bs4 import BeautifulSoup


class RollIt:
    def __init__(self, channel_link):
        self.channel_link = channel_link
        self.posts = []
        self.title = ''
        self.subs_num = ''
        self.desc = ''
        self.logo = ''
        self.links_num = ''
        self.photo_num = ''

    async def get_page(self, url):
        res = await loop.run_in_executor(None, requests.get, url)
        return res

    async def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        # Get title
        self.title = soup.find('div', class_='tgme_channel_info_header_title').text

        # Get number of subscribers
        self.subs_num = soup.find('div', class_='tgme_channel_info_counter') \
            .find('span', class_='counter_value').text

        # Get description
        self.desc = soup.find('div', class_='tgme_channel_info_description').text

        # Logo
        self.logo = soup.find('i', class_='tgme_page_photo_image').find('img')['src']

        # Get number of links
        self.links_num = soup.find_all('div', class_='tgme_channel_info_counter')[2] \
            .find('span', class_='counter_value').text

        # Get number of photos
        self.photo_num = soup.find_all('div', class_='tgme_channel_info_counter')[1] \
            .find('span', class_='counter_value').text

        all_widgets = soup.find_all('div', class_='tgme_widget_message_wrap')
        for piece in all_widgets[::-1]:
            link = piece.find('div', class_='tgme_widget_message').get('data-post')
            try:
                msg = piece.find('div', class_='tgme_widget_message_text').find('a').prettify()
            except:
                msg = piece.find('div', class_='tgme_widget_message_text').text
            try:
                vws = piece.find('span', class_='tgme_widget_message_views').text.strip()
            except:
                vws = 'No info or error'
            try:
                date = piece.find('time', class_='time')['datetime']
            except:
                date = 'No info or error'
            self.posts.append(
                {'link': link,
                 'message': msg,
                 'views': vws,
                 'date': date
                 }
            )

    async def get_channel_info(self):
        response = await self.get_page(self.channel_link)
        await self.parse_page(response)

    async def get_posts(self, quantity=None):
        await self.get_channel_info()

        posts_num = int(self.get_posts_num())
        while posts_num > 19:
            if quantity is not None and len(self.posts) >= quantity:
                break
            response = await self.get_page(f'{self.channel_link}?before={posts_num}')
            await self.parse_page(response)

            posts_num -= 20
            print(f"[+]{datetime.now().time()}: Parsed {len(self.posts)} posts")

    def get_posts_num(self):
        all_widgets = BeautifulSoup(requests.get(self.channel_link).text, 'lxml') \
            .find_all('div', class_='tgme_widget_message_wrap')
        get_number = all_widgets[-1].find('div', class_='tgme_widget_message').get('data-post').split('/')[-1]
        return get_number


async def main():
    channel_link = 'example-link'
    parser = RollIt(channel_link)
    await parser.get_posts(quantity=10)
    print("Title:", parser.title)
    print("Number of subscribers:", parser.subs_num)
    print("Description:", parser.desc)
    print("Logo:", parser.logo)
    print("Number of links:", parser.links_num)
    print("Number of photos:", parser.photo_num)
    print("Posts:", parser.posts)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())