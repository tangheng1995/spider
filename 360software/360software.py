#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from requests_html import HTMLSession
import pandas as pd
import asyncio

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost/360soft?charset=utf8"
db = SQLAlchemy(app)

class Soft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    desc = db.Column(db.String(250), nullable=False)
    size = db.Column(db.String(250), nullable=False)

db.create_all()
session = HTMLSession()

def write_to_csv(result):
    df=pd.DataFrame(result)
    df.to_csv('1.csv', mode='a', header=False, index=False)

async def get_category(category):
    category_tasks = []
    for c in category:
        category_name = c.text
        category_url = list(c.absolute_links)[0]
        coroutine1 = get_soft_list(category_url, category_name)
        category_tasks.append(asyncio.ensure_future(coroutine1))

    await asyncio.gather(*category_tasks)

async def get_soft_list(category_url,category_name):
    r = session.get(category_url)
    default_list = r.html.find('#listpage-list',first=True).find('dl')
    result = []
    for l in default_list[:10]:
        title = l.find('dd > div > strong > a', first=True).text
        # score = l.find('dd > div > em', first=True).text
        desc = l.find('dd > p', first=True).text
        size = l.find('dd > p')[1].text.split(' ')[2] + l.find('dd > p')[1].text.split(' ')[3]
        result.append([category_name,title,desc,size])
        soft = Soft(category_name=category_name,title=title,desc=desc,size=size)
        db.session.add(soft)
        db.session.commit()
    # write_to_csv(result)

async def main():
    r = session.get('http://baoku.360.cn/')
    category = r.html.find('#left-catalog-list', first=True).find('a')
    await asyncio.gather(get_category(category))


if __name__ == '__main__':
    asyncio.run(main())