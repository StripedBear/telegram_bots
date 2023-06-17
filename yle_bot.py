import asyncio
import re
from bs4 import BeautifulSoup as bs
import feedparser
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telegraph import Telegraph
import aiohttp


CHANNEL = 'yle_ru'


async def article_text(html):
    async with aiohttp.ClientSession() as session:
        htmlka = await session.get(html)
        soup = bs(await htmlka.text(), 'lxml')
    article_text = ''
    try:
        line = soup.find('section', class_='yle__article__content').find_all('p')  #.find_all('div') #find_all('p') #.find_all('div')
        for i in line:
            article_text += "<p>" + re.sub(r'(\(siirryt toiseen palveluun\))', '', i.text) + "</p>"
    except:
        pass
    
    return article_text


def get_updates():
    print('checking group')
    posts = client(GetHistoryRequest(
        peer=client.get_entity(CHANNEL), #
        limit=10,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0))
    clearly_posts = [i.message for i in posts.messages]
    return clearly_posts


def pic_and_title():
    print('parsing news')
    url = 'https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NOVOSTI'
    parsed = feedparser.parse(url)['entries'][:9]
    pics_list = []
    for i in parsed:
        if len(i['links'])>=2:
            link = i['links'][1]['href']
            link = re.sub(r'(?=https://images\.cdn\.yle\.fi/image/upload/).+/', 'https://images.cdn.yle.fi/image/upload/',
                   link)
            pics_list.append(link)
        else:
            pics_list.append('https://images.cdn.yle.fi/image/upload/39-42973859c268d07fd2f')
    titles = [i['title'] for i in parsed]
    link_list = [i['links'][0]['href'] for i in parsed]
    return [pics_list[::-1], titles[::-1], link_list[::-1]]


async def create_telegraph(pic, title, link):
    telegraph = Telegraph()
    telegraph.create_account(short_name='short_name')
    art_t = await article_text(link)
    main_image = f'<img src="{pic}" alt="{pic}">{art_t}<p>Оригинальная страница - {link}</p>'
    url = telegraph.create_page(
        title,
        author_name='Yle',
        html_content=main_image)["url"]
    return url


async def telegraph_and_telega(title):
    article = await create_telegraph(new_posts[0][new_posts[1].index(title)], title, new_posts[2][new_posts[1].index(title)])
    message = f'<a href="{article}">{title}</a>'
    await client.send_message(CHANNEL, message=message, parse_mode="HTML")


async def main():
    print('posting')
    tasks = []
    for title in new_posts[1]:
        if title not in old_posts:
            task = asyncio.create_task(telegraph_and_telega(title))
            tasks.append(task)
    await asyncio.gather(*tasks)
    print('Done!')



if __name__ == "__main__":
    api_id = 000000
    api_hash = ''
    phone = ''

    client = TelegramClient('anon', api_id, api_hash)
    with client:
        old_posts = get_updates()
        new_posts = pic_and_title()
        client.loop.run_until_complete(main())
