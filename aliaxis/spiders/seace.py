import scrapy


class SeaceSpider(scrapy.Spider):
    name = 'seace'
    allowed_domains = ['https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml']
    start_urls = ['http://https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml/']

    def parse(self, response):
        pass
