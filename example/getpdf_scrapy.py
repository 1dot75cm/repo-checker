from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from tutorial.items import FolioItem

class FolioSpider(CrawlSpider):
    name = "getpdf"
    allowed_domains = ["folio.co.in"]
    start_urls = ["http://folio.co.in/categories/"]
    rules = (
        Rule(LinkExtractor(allow=('/categories/.*?/')), 'parse_category', follow=True),
        #Rule(LinkExtractor(allow=('/itbooks/.*/')), 'parse_pdf'),
        Rule(LinkExtractor(allow=('\?page=\d+')))
    )

    def parse_pdf(self, response, category):
        item = FolioItem()
        item['name'] = response.xpath('//div[@class="row"]//h1//text()').extract_first().strip()
        item['link'] = response.css('div.row a::attr(href)').extract_first().strip()
        item['category'] = category
        with open('test.log', 'a+') as f:
            body = '%s, %s, %s' % (item['name'], category, item['link'])
            f.write(body + '\n')
        return item

    def parse_category(self, response):
        urls = response.css('div.hide-on-small-only a::attr(href)').extract()
        categor = response.css('div.container h1::text').re('(.*)\s')[0]
        for url in urls:
            url = 'http://folio.co.in' + url
            yield Request(url, callback=lambda response, category=None: self.parse_pdf(response, categor))
