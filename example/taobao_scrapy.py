# Get all product information for taobao.com

from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from tutorial.items import TaobaoItem
import json

class TaobaoSpider(CrawlSpider):
    name = "taobao"
    allowed_domains = ["taobao.com"]
    start_urls = ["https://s.taobao.com/list?seller_type=taobao&json=on"]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, self.parse_item, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux; rv:47.0) Gecko/20100101 Firefox/47.0"
            })

    def parse_item(self, response):
        d = json.loads(response.body.decode())
        if 'common' in d['mods']['nav']['data']:
            for i in d['mods']['nav']['data']['common'][0]['sub']:
                url = self.start_urls[0] + "&cat=%s" % i['value']
                yield Request(url, callback=self.parse_item)
        else:
            output, filename = '', ''
            pv = d['mods']['pager']['data']['currentPage'] * d['mods']['pager']['data']['pageSize']
            url = self.start_urls[0] + "&cat=%s&s=%s" % (
                d['mods']['nav']['data']['breadcrumbs']['catpath'][-1]['value'],
                pv)
            for item in d['mods']['itemlist']['data']['auctions']:
                output += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                        item['category'],
                        item['user_id'],
                        item['nick'],
                        item['nid'],
                        item['title'],
                        item['item_loc'],
                        item['reserve_price'],
                        item['view_price'],
                        item['detail_url'],
                        item['shopLink'])
            for i in d['mods']['nav']['data']['breadcrumbs']['catpath']:
                filename += '%s.'%i['name']
            with open(filename.replace('/','_')+'csv', 'a+') as f:
                f.write(output)
            yield Request(url, callback=self.parse_item)
