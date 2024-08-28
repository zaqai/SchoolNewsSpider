# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import email.utils
import json
import os
import smtplib
from email.mime.text import MIMEText

import openpyxl
import pymysql
import requests
import yaml


class SchoolNewsExcelPipeline:
    def __init__(self) -> None:
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.title = 'movie'
        self.ws.append(['title', 'time', 'url', 'content', 'source'])

    def close_spider(self, spider):
        self.wb.save('movie.xlsx')

    def process_item(self, item, spider):
        title = item.get('title', '')
        time = item.get('time', '')
        url = item.get('url', '')
        content = item.get('content', '')
        source = item.get('source', '')
        self.ws.append([title, time, url, content, source])
        return item


class SchoolNewsDbPipeline:
    def __init__(self) -> None:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        db_host = os.getenv('DB_HOST', config['database']['host'])
        db_user = os.getenv('DB_USER', config['database']['user'])
        db_password = os.getenv('DB_PASSWORD', config['database']['password'])
        db_name = os.getenv('DB_NAME', config['database']['database'])
        db_port = os.getenv('DB_NAME', config['database']['port'])
        self.conn = pymysql.connect(
            host=db_host,
            user=db_user,
            port=db_port,
            password=db_password,
            database=db_name,
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        self.map_table = {
            "https://se.xjtu.edu.cn/xwgg/tzgg.htm": "xjtuse_tzgg",
            "https://se.xjtu.edu.cn/xwgg/xwxx.htm": "xjtuse_xwxx",
            "https://se.xjtu.edu.cn/rcpy/yjspy/yjsjw.htm": "xjtuse_yjsjw",
            "https://se.xjtu.edu.cn/sxjy.htm": "xjtuse_sxjy",
            "https://gs.xjtu.edu.cn/tzgg.htm": "xjtugs_tzgg",
        }

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        title = item.get('title', '')
        time = item.get('time', '')
        url = item.get('url', '')
        content = item.get('content', '')
        source = item.get('source', '')
        self.cursor.execute(f"select url from {self.map_table[source]} ORDER BY insert_time DESC LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            DB_url = result[0]
            if DB_url != url:
                self.cursor.execute(
                    f"insert into {self.map_table[source]}(title, time, url, content, source) values(%s, %s, %s, %s, %s)",
                    [title, time, url, content, source])
                push({'title': title, 'url': url, 'content': content})
        else:
            print("No data found.")

        return item


def push(data):
    pass
