from urllib.parse import urljoin

import scrapy
from scrapy import Request, Selector
from scrapy.http import HtmlResponse

from school_news.items import SchoolNewsItem


class XjtuSpider(scrapy.Spider):
    name = "xjtu"
    allowed_domains = ["xjtu.edu.cn"]

    def start_requests(self):
        urls = [
            "https://se.xjtu.edu.cn/xwgg/tzgg.htm",
            "https://se.xjtu.edu.cn/xwgg/xwxx.htm",
            "https://se.xjtu.edu.cn/rcpy/yjspy/yjsjw.htm",
            "https://se.xjtu.edu.cn/sxjy.htm"
        ]
        for url in urls:
            if 'xwxx' in url:
                # 这个页面规则与其他不同
                yield Request(url, callback=self.parse_xwxx)
            else:
                yield Request(url)
        yield Request('https://gs.xjtu.edu.cn/tzgg.htm', callback=self.parse_gs)

    def parse(self, response):
        sel = Selector(response)
        list_items = sel.css("div.txtList > ul > li > a")
        # 假定数据库已存在之前的数据, 只需要查询最新的一条数据
        item = list_items[0]

        schoolNewsItem = SchoolNewsItem()
        title = item.css("a > p.txt::text").extract_first()
        time = item.css("a > p.time > span::text").extract_first()
        url = item.css("a::attr(href)").extract_first()
        base_url = response.url
        detail_url = urljoin(base_url, url)
        schoolNewsItem['title'] = title
        schoolNewsItem['time'] = time
        schoolNewsItem['url'] = detail_url
        schoolNewsItem['source'] = base_url
        yield Request(detail_url, callback=self.parse_detail, cb_kwargs={'item': schoolNewsItem})

    def parse_xwxx(self, response):
        sel = Selector(response)
        list_items = sel.css("div.imgList > ul > li > a")
        # 假定数据库已存在之前的数据, 只需要查询最新的一条数据
        item = list_items[0]
        schoolNewsItem = SchoolNewsItem()
        title = item.css("a::attr(title)").extract_first()
        year_month = item.css("a > p.time::text").extract_first()
        day = item.css("a > p.time span::text").extract_first()
        time = year_month + '-' + day
        url = item.css("a::attr(href)").extract_first()
        base_url = response.url
        detail_url = urljoin(base_url, url)
        schoolNewsItem['title'] = title
        schoolNewsItem['time'] = time
        schoolNewsItem['url'] = detail_url
        schoolNewsItem['source'] = base_url
        yield Request(detail_url, callback=self.parse_detail, cb_kwargs={'item': schoolNewsItem})

    def parse_gs(self, response):
        sel = Selector(response)
        list_items = sel.css("div.list_right_con > ul > li")
        # 假定数据库已存在之前的数据, 只需要查询最新的一条数据
        item = list_items[0]
        schoolNewsItem = SchoolNewsItem()
        title = item.css("li > a::attr(title)").extract_first()
        time = item.css("li > span::text").extract_first()
        url = item.css("li > a::attr(href)").extract_first()
        base_url = response.url
        detail_url = urljoin(base_url, url)
        schoolNewsItem['title'] = title
        schoolNewsItem['time'] = time
        schoolNewsItem['url'] = detail_url
        schoolNewsItem['source'] = base_url
        yield Request(detail_url, callback=self.parse_gsdetail, cb_kwargs={'item': schoolNewsItem})

    def parse_detail(self, response: HtmlResponse, **kwargs):
        schoolNewsItem = kwargs['item']
        # 这种方式可以实现提取一个标签下的所有纯文本
        content = "".join(response.xpath('//div[@class="conSub"]//text()').extract())
        schoolNewsItem['content'] = content
        yield schoolNewsItem

    def parse_gsdetail(self, response: HtmlResponse, **kwargs):
        schoolNewsItem = kwargs['item']
        # 这种方式可以实现提取一个标签下的所有纯文本
        content = "".join(response.xpath('//form[@name="_newscontent_fromname"]//text()').extract())
        schoolNewsItem['content'] = content
        yield schoolNewsItem
