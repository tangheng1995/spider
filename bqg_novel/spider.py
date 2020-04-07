#!/usr/bin/env python
# encoding: utf-8
'''
@author: Archer
@license: (C) Copyright 2013-2019, Brook.
@contact: 347420070@qq.com
@software: Pycharm
@file: spider.py
@time: 2019/8/3 下午8:40
@desc:
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from requests_html import HTMLSession
import asyncio

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
db = SQLAlchemy(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String, unique=True, nullable=False)
    category_url = db.Column(db.String, unique=True, nullable=False)


class Novel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    novel_name = db.Column(db.String(80), nullable=False)
    novel_creator = db.Column(db.String(80), nullable=False)
    introduction = db.Column(db.String(500), nullable=False)
    novel_image_url = db.Column(db.String(500), nullable=False)
    novel_url = db.Column(db.String(250), unique=True, nullable=False)
    status = db.Column(db.String(80), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('novel', lazy=True))


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_name = db.Column(db.String(80), nullable=False)
    chapter_url = db.Column(db.String(500), unique=True, nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    novel = db.relationship('Novel', backref=db.backref('chapter', lazy=True))


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_pre_url = db.Column(db.String(500), unique=True, nullable=False)
    chapters_url = db.Column(db.String(500), nullable=False)
    chapter_next_url = db.Column(db.String(500), unique=True, nullable=False)
    content = db.Column(db.String(), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    chapter = db.relationship('Chapter', backref=db.backref('content', lazy=True))
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    novel = db.relationship('Novel', backref=db.backref('content', lazy=True))


db.create_all()

session = HTMLSession()


async def get_category(category):
    category_tasks = []
    for c in category:
        category_name = c.text
        category_url = list(c.absolute_links)[0]
        category_object = Category(category_name=category_name, category_url=category_url)
        coroutine1 = get_hot_content(category_url, category_object)
        category_tasks.append(asyncio.ensure_future(coroutine1))

    await asyncio.gather(*category_tasks)


async def get_hot_content(category_url, category_object):
    r = session.get(category_url)
    # 火热区
    if r.html.find('#hotcontent > div', first=True) != None:
        hot_content = r.html.find('#hotcontent > div', first=True).find('div.item')

        hot_content_tasks = []
        for h in hot_content:
            novel_name = h.find('dl > dt > a', first=True).text
            novel_creator = h.find('span', first=True).text
            introduction = h.find('dd', first=True).text
            novel_image_url = list(h.find('div.image > a > img[src]'))[0].attrs['src']
            novel_url = list(h.find('div.image > a')[0].absolute_links)[0]

            r = session.get(novel_url)
            status = r.html.find('#info > p:nth-child(3)')[0].text.split('：')[1].split(',')[0]

            novel_object = Novel(novel_name=novel_name, novel_creator=novel_creator, introduction=introduction,
                                 novel_image_url=novel_image_url, novel_url=novel_url, status=status,
                                 category=category_object)

            coroutine2 = get_chapter(novel_url, novel_object, category_object)
            hot_content_tasks.append(asyncio.ensure_future(coroutine2))
        await asyncio.gather(*hot_content_tasks)


async def get_chapter(novel_url, novel_object, category_object):
    r = session.get(novel_url)
    # 获取章节
    if r.html.find('#list > dl', first=True) != None:
        chapter_list = r.html.find('#list > dl', first=True).find('dd')
        chapter_tasks = []
        for ch in chapter_list:
            chapter_name = ch.find('a', first=True).text
            chapter_url = list(ch.find('a', first=True).absolute_links)[0]
            chapter_object = Chapter(chapter_name=chapter_name, chapter_url=chapter_url, novel=novel_object)
            coroutine3 = get_content(chapter_url, chapter_object, novel_object, category_object)
            chapter_tasks.append(asyncio.ensure_future(coroutine3))
        await asyncio.gather(*chapter_tasks)


async def get_content(chapter_url, chapter_object, novel_object, category_object):
    # 获取章节内容
    r = session.get(chapter_url)
    if r.html.find('#wrapper > div.content_read > div > div.bookname > div.bottem1') != None:
        chapter_list = r.html.find('#wrapper > div.content_read > div > div.bookname > div.bottem1')[0].find('a')
        chapter_pre_url = list(chapter_list[0].absolute_links)[0]
        chapters_url = list(chapter_list[1].absolute_links)[0]
        chapter_next_url = list(chapter_list[2].absolute_links)[0]

        content = r.html.find('#content', first=True).text

        Content(chapter_pre_url=chapter_pre_url, chapters_url=chapters_url,
                chapter_next_url=chapter_next_url, content=content, chapter=chapter_object, novel=novel_object)

        db.session.add(category_object)
        db.session.commit()


async def main():
    r = session.get('https://www.biquge.com.cn')
    category = r.html.find('#wrapper > div.nav > ul', first=True).find('a')
    await asyncio.gather(get_category(category))


if __name__ == '__main__':
    asyncio.run(main())
