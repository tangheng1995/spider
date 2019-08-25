async def get_content(chapter_url,chapter_object,novel_object,category_object):
    # 获取章节内容
    r = session.get(chapter_url)
    chapter_list = r.html.find('#wrapper > div.content_read > div > div.bookname > div.bottem1')[0].find('a')
    chapter_pre_url = list(chapter_list[0].absolute_links)[0]
    chapters_url = list(chapter_list[1].absolute_links)[0]
    chapter_next_url = list(chapter_list[2].absolute_links)[0]

    content = r.html.find('#content', first=True).text

    content_object = Content(chapter_pre_url=chapter_pre_url, chapters_url=chapters_url,
                             chapter_next_url=chapter_next_url, content=content, chapter=chapter_object)

    db.session.add(category_object)
    db.session.commit()

async def get_chapter(novel_url,category_object):
    # 获取小说更新状态
    r = session.get(novel_url)
    status = r.html.find('#info > p:nth-child(3)')[0].text.split('：')[1].split(',')[0]

    novel_object = Novel(novel_name=novel_name, novel_creator=novel_creator, introduction=introduction,
                         novel_image_url=novel_image_url, novel_url=novel_url, status=status,
                         category=category_object)

    # 获取章节
    chapter_list = r.html.find('#list > dl', first=True).find('dd')
    for ch in chapter_list:
        chapter_name = ch.find('a', first=True).text
        chapter_url = list(ch.find('a', first=True).absolute_links)[0]
        chapter_object = Chapter(chapter_name=chapter_name, chapter_url=chapter_url, novel=novel_object)

        # # 获取章节内容
        # r = session.get(chapter_url)
        # chapter_list = r.html.find('#wrapper > div.content_read > div > div.bookname > div.bottem1')[0].find('a')
        # chapter_pre_url = list(chapter_list[0].absolute_links)[0]
        # chapters_url = list(chapter_list[1].absolute_links)[0]
        # chapter_next_url = list(chapter_list[2].absolute_links)[0]
        #
        # content = r.html.find('#content', first=True).text
        #
        # content_object = Content(chapter_pre_url=chapter_pre_url, chapters_url=chapters_url,
        #                          chapter_next_url=chapter_next_url, content=content, chapter=chapter_object)
        #
        # db.session.add(category_object)
        # db.session.commit()


async def get_category():
    r = session.get('https://www.biquge.com.cn')

    category = r.html.find('#wrapper > div.nav > ul', first=True).find('a')
    for c in category:
        category_name = c.text
        category_url = list(c.absolute_links)[0]
        category_object = Category(category_name=category_name, category_url=category_url)

        # db.session.add(category_object)
        # db.session.commit()

        r = session.get(category_url)
        # 火热区
        hot_content = r.html.find('#hotcontent > div', first=True).find('div.item')
        for h in hot_content:
            novel_name = h.find('dl > dt > a', first=True).text
            novel_creator = h.find('span', first=True).text
            introduction = h.find('dd', first=True).text
            novel_image_url = list(h.find('div.image > a > img[src]'))[0].attrs['src']
            novel_url = list(h.find('div.image > a')[0].absolute_links)[0]