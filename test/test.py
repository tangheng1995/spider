import unittest
from requests_html import HTMLSession
from spider.spider import *

session = HTMLSession()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


class TestGetPage(unittest.TestCase):
    def test_get_page(self):
        url = 'https://www.biquge.com.cn/xuanhuan/'
        r = session.get(url)
        # 火热区
        hot_content = r.html.find('#hotcontent > div.ll', first=True).find('div.item')
        print(hot_content)
        for h in hot_content:
            novel_name = h.find('dl > dt > a', first=True).text
            novel_creator = h.find('span', first=True).text
            introduction = h.find('dd', first=True).text
            novel_image_url = list(h.find('div.image > a > img[src]'))[0].attrs['src']
            novel_url = list(h.find('div.image > a')[0].absolute_links)[0]
            print(novel_image_url)

    def test_get_chapter(self):
        url = 'https://www.biquge.com.cn/book/30732/'
        r = session.get(url)
        status = r.html.find('#info > p:nth-child(3)')[0].text.split('：')[1].split(',')[0]
        chapter_list = r.html.find('#list > dl', first=True).find('dd')
        for ch in chapter_list:
            chapter_name = ch.find('a', first=True).text
            chapter_url = list(ch.find('a', first=True).absolute_links)[0]
            print(chapter_name)

    def test_get_content(self):
        url = 'https://www.biquge.com.cn/book/30732/111846.html'
        r = session.get(url)
        chapter_list = r.html.find('#wrapper > div.content_read > div > div.bookname > div.bottem1')[0].find('a')
        print(chapter_list)
        chapter_pre_url = list(chapter_list[0].absolute_links)[0]
        chapter_url = list(chapter_list[1].absolute_links)[0]
        chapter_next_url = list(chapter_list[2].absolute_links)[0]
        print(chapter_next_url)
        # content = r.html.find('#content', first=True).text
        # print(content)

    def test_get_category(self):
        category = Category.query.all()
        print(category)

    def test_get_novel(self):
        novel = Novel.query.all()
        print(novel)

    def test_get_chapter(self):
        chapter = Chapter.query.all()
        print(chapter)

    def test_get_content(self):
        content = Content.query.all()
        print(content)


if __name__ == '__main__':
    unittest.main()
